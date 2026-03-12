import os
import sys

# Adaptação para Vercel Serverless: Adiciona a pasta do main.py ao Path do Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, BackgroundTasks, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from services.db_service import criar_vaga, salvar_configuracoes, obter_vagas_ativas, supabase, limpar_sessao
from services.ai_service import gerar_resposta_ia, transcrever_audio_zapi, gerar_audio_ia
from services.zapi_service import enviar_mensagem_texto, enviar_audio
from services.email_service import verificar_novos_curriculos
from services.scoring_service import calcular_lead_scoring

load_dotenv()

app = FastAPI(title="Agente IA Seleção Mvp")

# Configurar CORS (Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginInput(BaseModel):
    email: str
    password: str

@app.post("/api/auth/login")
async def endpoint_login(req: LoginInput):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": req.email,
            "password": req.password,
        })
        return {"status": "success", "data": response.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/api/vagas")
async def endpoint_obter_vagas():
    vagas = obter_vagas_ativas()
    return {"status": "success", "data": vagas}


class VagaInput(BaseModel):
    titulo: str
    descricao: str
    requisitos: str

class ConfigInput(BaseModel):
    email: str
    whatsapp: str

@app.post("/api/vagas")
async def endpoint_criar_vaga(vaga: VagaInput):
    dados = {
        "titulo": vaga.titulo,
        "descricao": vaga.descricao,
        "empresa": "Sua Empresa",
        "responsavel_email": "admin@empresa.com",
    }
    novo_id = criar_vaga(dados)
    return {"status": "success", "id": novo_id}

@app.post("/api/configuracoes")
async def endpoint_salvar_configs(config: ConfigInput):
    salvar_configuracoes(config.email, config.whatsapp)
    return {"status": "success"}
@app.post("/api/upload-cv")
async def endpoint_upload_cv(file: UploadFile = File(...)):
    # Simulação: Na prática, usaria PyPDF2 para extrair texto do 'file' real.
    texto_curriculo = f"Extraído de: {file.filename}. Experiência prêvia em UI/UX e desenvolvimento frontend."
    
    # Executa o Lead Scoring Mock ou Real dependendo da OpenAI API Key (Vaga chumbada para MVP)
    resultado = calcular_lead_scoring(
        texto_curriculo=texto_curriculo,
        titulo_vaga="UX Designer",
        descricao_vaga="Precisamos de um Senior UX Designer para o nosso time.",
        requisitos_vaga="Experiência em UI/UX, Figma e prototipagem rápida."
    )
    
    return {"status": "success", "scoring": resultado}

# Cache de mensagens processadas para evitar duplicidade (Idempotência)
processed_messages = []

@app.post("/webhook/zapi")
async def zapi_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    
    # Extrai o ID da mensagem para evitar processamento duplicado (Webhook Retry)
    message_id = payload.get("messageId", "")
    if message_id and message_id in processed_messages:
        return {"status": "already_processed"}
    
    if message_id:
        processed_messages.append(message_id)
        if len(processed_messages) > 100:
            processed_messages.pop(0)

    # Verifica se a mensagem de texto chegou e se NÃO foi enviada pela própria IA (fromMe)
    if "isGroup" in payload and not payload["isGroup"] and not payload.get("fromMe", False):
        remetente = payload.get("phone", "")
        
        # 1. Tentar extrair Texto ou Áudio
        texto_recebido = payload.get("text", {}).get("message", "")
        audio_recebido = payload.get("audio", {}).get("audioUrl", "")
        
        # Flag para saber se precisamos responder em áudio
        responder_audio = False

        if audio_recebido:
            print(f"Áudio recebido de {remetente}: {audio_recebido}")
            texto_transcrito = transcrever_audio_zapi(audio_recebido)
            if texto_transcrito:
                texto_recebido = texto_transcrito
                responder_audio = True
            
        if texto_recebido:
            # Comando especial: limpar memória/histórico da conversa
            if texto_recebido.strip() == "#limpar":
                limpar_sessao(remetente)
                enviar_mensagem_texto(remetente, "✅ Conversa reiniciada! Me manda um 'oi' para começarmos de novo.")
                return {"status": "cleared"}

            # Validação automática de CEP: se a mensagem parecer um CEP, consulta ViaCEP
            import re
            cep_match = re.fullmatch(r"\d{5}-?\d{3}", texto_recebido.strip())
            if cep_match:
                dados_cep = consultar_viacep(texto_recebido.strip())
                if dados_cep:
                    cidade = dados_cep.get("localidade", "")
                    uf = dados_cep.get("uf", "")
                    bairro = dados_cep.get("bairro", "")
                    logradouro = dados_cep.get("logradouro", "")
                    endereco_formatado = f"{logradouro}, {bairro} - {cidade}/{uf}".strip(", ")
                    texto_recebido = f"{texto_recebido.strip()} [SISTEMA: CEP válido. Endereço encontrado: {endereco_formatado}]"
                else:
                    texto_recebido = f"{texto_recebido.strip()} [SISTEMA: CEP inválido ou não encontrado. Peça ao candidato que informe um CEP válido de 8 dígitos.]"

            # Resposta IA normal de RH
            resposta_texto = gerar_resposta_ia(texto_recebido, remetente)
            
            # 2. Verifica se a entrevista acabou
            if "[FIM_ENTREVISTA]" in resposta_texto:
                # Remove a tag para não aparecer para o usuário
                resposta_texto = resposta_texto.replace("[FIM_ENTREVISTA]", "").strip()
                
                # Dispara processamento em background para extrair dados e colocar na dashboard
                background_tasks.add_task(processar_final_candidatura, remetente)
                print(f"Entrevista finalizada para {remetente}. Processando dados do candidato...")
            
            # 3. Lógica para Responder usando Textos ou VOZ
            if "[AUDIO]" in resposta_texto:
                responder_audio = True
                resposta_texto = resposta_texto.replace("[AUDIO]", "").strip()

            if responder_audio:
                # Primeiro tenta gerar o audio
                try:
                    arquivo_audio = gerar_audio_ia(resposta_texto, f"/tmp/response_{remetente}.mp3")
                    if arquivo_audio:
                        enviar_audio(remetente, arquivo_audio)
                        # Opcional: apagar o arquivo da temp
                        import os
                        if os.path.exists(arquivo_audio):
                            os.remove(arquivo_audio)
                    else:
                        print(f"Falha ao gerar áudio para {remetente}. Enviando texto como fallback.")
                        enviar_mensagem_texto(remetente, resposta_texto)
                except Exception as e:
                    print(f"Erro no processamento de áudio: {e}")
                    enviar_mensagem_texto(remetente, resposta_texto)
            else:
                # 3b. Enviar no Zap via Texto padrão
                enviar_mensagem_texto(remetente, resposta_texto)
            
    return {"status": "received"}

@app.get("/api/candidaturas")
async def endpoint_obter_candidaturas():
    if not supabase:
        return {"status": "error", "data": []}
    res = supabase.table("candidaturas").select(
        "*, candidatos(nome, whatsapp, cpf_raw, endereco_completo, cargo_desejado, curriculo_texto_extraido, fonte), vagas(titulo)"
    ).order("created_at", desc=True).execute()
    return {"status": "success", "data": res.data or []}

def consultar_viacep(cep: str) -> dict | None:
    """Consulta o ViaCEP e retorna os dados de endereço ou None se inválido."""
    import re, requests
    cep_limpo = re.sub(r"\D", "", cep)
    if len(cep_limpo) != 8:
        return None
    try:
        resp = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
        data = resp.json()
        if data.get("erro"):
            return None
        return data
    except Exception:
        return None

@app.get("/api/verificar_emails")
async def endpoint_verificar_emails():
    # Rota para disparar manualmente ou agendada
    total_baixados = verificar_novos_curriculos()
    return {"novos_curriculos": total_baixados}

async def processar_final_candidatura(remetente: str):
    """
    Extrai dados da conversa, salva o candidato e cria a candidatura vinculada à vaga.
    """
    from services.db_service import obter_sessao, supabase
    from services.ai_service import obter_client_openai
    from services.scoring_service import calcular_lead_scoring
    import json

    print(f"Iniciando extração de dados para o remetente: {remetente}")
    sessao = obter_sessao(remetente)
    if not sessao:
        print("Sessão não encontrada para extração.")
        return

    historico = sessao.get("dados_candidato", {}).get("historico_ia", [])
    if not historico:
        print("Histórico vazio, abortando extração.")
        return

    # 1. Extrair JSON do Candidato via LLM
    client = obter_client_openai()
    if not client: return
    
    prompt_extracao = f"""
    Você é um extrator de dados. Analise o histórico da conversa de recrutamento abaixo e retorne APENAS um JSON puro.
    Campos necessários:
    - nome (Nome completo do candidato)
    - cpf (Apenas números)
    - cep (Localização informada)
    - experiencia_resumo (Resumo do que ele contou sobre a experiência profissional dele)
    - vaga_desejada_titulo (Título da vaga que ele escolheu durante a conversa)
    
    HISTÓRICO:
    {json.dumps(historico[-15:])}
    """
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_extracao}],
            temperature=0
        )
        conteudo = resp.choices[0].message.content.strip().replace("```json", "").replace("```", "")
        dados_extracao = json.loads(conteudo)
        
        # 2. Salvar/Atualizar Candidato no Supabase
        candidato_id = None
        # Tenta buscar por WhatsApp
        check = supabase.table("candidatos").select("id").eq("whatsapp", remetente).execute()
        
        payload_candidato = {
            "nome": dados_extracao.get("nome"),
            "whatsapp": remetente,
            "cpf_raw": dados_extracao.get("cpf"),
            "endereco_completo": dados_extracao.get("cep"),
            "cargo_desejado": dados_extracao.get("vaga_desejada_titulo"),
            "curriculo_texto_extraido": dados_extracao.get("experiencia_resumo"),
            "fonte": "whatsapp",
            "updated_at": "now()"
        }

        if check.data:
            candidato_id = check.data[0]["id"]
            supabase.table("candidatos").update(payload_candidato).eq("id", candidato_id).execute()
        else:
            res_c = supabase.table("candidatos").insert(payload_candidato).execute()
            if res_c.data:
                candidato_id = res_c.data[0]["id"]

        # 3. Vincular Candidatura à Vaga correspondente
        if candidato_id:
            vaga_titulo = dados_extracao.get("vaga_desejada_titulo", "")
            # Busca vaga ativa por título aproximado
            vaga_res = supabase.table("vagas").select("*").ilike("titulo", f"%{vaga_titulo}%").eq("status", "aberta").execute()
            
            if vaga_res.data:
                vaga_obj = vaga_res.data[0]
                vaga_id = vaga_obj["id"]
                
                # Calcular Scoring Real em background (não mostra pro usuário)
                score_data = calcular_lead_scoring(
                    texto_curriculo=dados_extracao.get("experiencia_resumo", ""),
                    titulo_vaga=vaga_obj["titulo"],
                    descricao_vaga=vaga_obj["descricao"],
                    requisitos_vaga=str(vaga_obj.get("requisitos_obrigatorios", ""))
                )
                
                # Upsert na tabela candidaturas para aparecer no dashboard
                supabase.table("candidaturas").upsert({
                    "candidato_id": candidato_id,
                    "vaga_id": vaga_id,
                    "score_final": score_data.get("score", 0),
                    "justificativa_ia": score_data.get("justificativa"),
                    "pontos_fortes": score_data.get("pontos_fortes", []),
                    "pontos_atencao": score_data.get("pontos_fracos", []),
                    "status": "triagem"
                }, on_conflict="candidato_id, vaga_id").execute()
                
                print(f"SUCESSO: Candidatura vinculada na Dashboard para {remetente} na vaga {vaga_titulo}")
            else:
                print(f"AVISO: Vaga '{vaga_titulo}' não encontrada ou não está aberta.")

    except Exception as e:
        print(f"ERRO CRÍTICO no processamento final da candidatura: {e}")
