import os
import sys

# Adaptação para Vercel Serverless: Adiciona a pasta do main.py ao Path do Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from services.db_service import criar_vaga, salvar_configuracoes, obter_vagas_ativas, supabase, limpar_sessao, mensagem_ja_processada, marcar_mensagem_processada
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

@app.post("/webhook/zapi")
async def zapi_webhook(request: Request):
    payload = await request.json()

    # Verifica se a mensagem de texto chegou e se NÃO foi enviada pela própria IA (fromMe)
    if "isGroup" in payload and not payload["isGroup"] and not payload.get("fromMe", False):
        remetente = payload.get("phone", "")
        message_id = payload.get("messageId", "")

        # Deduplicação via Supabase — funciona em serverless (sem estado em memória)
        if message_id and mensagem_ja_processada(remetente, message_id):
            return {"status": "already_processed"}
        if message_id:
            marcar_mensagem_processada(remetente, message_id)
        
        # 1. Tentar extrair Texto, Áudio ou Documento (PDF)
        texto_recebido = payload.get("text", {}).get("message", "")
        audio_recebido = payload.get("audio", {}).get("audioUrl", "")
        documento_recebido = payload.get("document", {}).get("documentUrl", "")
        documento_mime = payload.get("document", {}).get("mimeType", "")

        # Flag para saber se precisamos responder em áudio
        responder_audio = False

        if audio_recebido:
            print(f"Áudio recebido de {remetente}: {audio_recebido}")
            texto_transcrito = transcrever_audio_zapi(audio_recebido)
            if texto_transcrito:
                texto_recebido = texto_transcrito
                responder_audio = True

        if documento_recebido:
            mime = documento_mime.lower()
            nome_arquivo = payload.get("document", {}).get("fileName", "").lower()
            is_pdf = "pdf" in mime or nome_arquivo.endswith(".pdf")
            is_word = "wordprocessingml" in mime or "msword" in mime or nome_arquivo.endswith((".docx", ".doc"))

            if is_pdf:
                print(f"PDF recebido de {remetente}: {documento_recebido}")
                texto_curriculo = extrair_texto_pdf_url(documento_recebido)
            elif is_word:
                print(f"Word recebido de {remetente}: {documento_recebido}")
                texto_curriculo = extrair_texto_word_url(documento_recebido)
            else:
                texto_curriculo = ""

            if texto_curriculo:
                texto_recebido = f"[CURRÍCULO ENVIADO PELO CANDIDATO]\n{texto_curriculo[:3000]}"
            elif is_pdf or is_word:
                texto_recebido = "[SISTEMA: O candidato enviou um documento, mas não foi possível extrair o texto. Peça para ele copiar e colar as principais informações do currículo na conversa.]"
            
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
            fim_entrevista = False
            if "[FIM_ENTREVISTA]" in resposta_texto:
                resposta_texto = resposta_texto.replace("[FIM_ENTREVISTA]", "").strip()
                fim_entrevista = True
                print(f"Entrevista finalizada para {remetente}.")

            # 3. Lógica para Responder usando Textos ou VOZ
            if "[AUDIO]" in resposta_texto:
                responder_audio = True
                resposta_texto = resposta_texto.replace("[AUDIO]", "").strip()

            if responder_audio:
                try:
                    arquivo_audio = gerar_audio_ia(resposta_texto, f"/tmp/response_{remetente}.mp3")
                    if arquivo_audio:
                        enviar_audio(remetente, arquivo_audio)
                        import os
                        if os.path.exists(arquivo_audio):
                            os.remove(arquivo_audio)
                    else:
                        enviar_mensagem_texto(remetente, resposta_texto)
                except Exception as e:
                    print(f"Erro no processamento de áudio: {e}")
                    enviar_mensagem_texto(remetente, resposta_texto)
            else:
                enviar_mensagem_texto(remetente, resposta_texto)

            # 4. Processa candidatura APÓS enviar resposta ao candidato.
            # Executado de forma síncrona (await) para garantir execução em ambientes
            # serverless (Vercel), onde background_tasks são encerrados com a resposta HTTP.
            if fim_entrevista:
                await processar_final_candidatura(remetente)
            
    return {"status": "received"}

@app.get("/api/candidaturas")
async def endpoint_obter_candidaturas():
    if not supabase:
        return {"status": "error", "data": []}

    candidaturas = supabase.table("candidaturas").select("*").order("created_at", desc=True).execute().data or []
    if not candidaturas:
        return {"status": "success", "data": []}

    # Bulk lookup de candidatos e vagas (sem depender de FK no Supabase)
    candidato_ids = list({c["candidato_id"] for c in candidaturas if c.get("candidato_id")})
    vaga_ids      = list({c["vaga_id"]      for c in candidaturas if c.get("vaga_id")})

    candidatos_map = {}
    if candidato_ids:
        rows = supabase.table("candidatos").select(
            "id, nome, whatsapp, endereco_completo, cargo_desejado, curriculo_texto_extraido, fonte"
        ).in_("id", candidato_ids).execute().data or []
        candidatos_map = {r["id"]: r for r in rows}

    vagas_map = {}
    if vaga_ids:
        rows = supabase.table("vagas").select("id, titulo").in_("id", vaga_ids).execute().data or []
        vagas_map = {r["id"]: r for r in rows}

    for c in candidaturas:
        c["candidatos"] = candidatos_map.get(c.get("candidato_id"), {})
        c["vagas"]      = vagas_map.get(c.get("vaga_id"), {})

    return {"status": "success", "data": candidaturas}

def extrair_texto_pdf_url(url: str) -> str:
    """Baixa um PDF de uma URL e extrai o texto usando PyPDF2."""
    import requests, io, PyPDF2
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        reader = PyPDF2.PdfReader(io.BytesIO(resp.content))
        texto = ""
        for page in reader.pages:
            texto += page.extract_text() or ""
        return texto.strip()
    except Exception as e:
        print(f"Erro ao extrair PDF: {e}")
        return ""

def extrair_texto_word_url(url: str) -> str:
    """Baixa um .docx de uma URL e extrai o texto usando python-docx."""
    import requests, io, docx
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        doc = docx.Document(io.BytesIO(resp.content))
        texto = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return texto.strip()
    except Exception as e:
        print(f"Erro ao extrair Word: {e}")
        return ""

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
        
        from datetime import datetime, timezone
        payload_candidato = {
            "nome": dados_extracao.get("nome"),
            "whatsapp": remetente,
            "cpf_raw": dados_extracao.get("cpf"),
            "endereco_completo": dados_extracao.get("cep"),
            "cargo_desejado": dados_extracao.get("vaga_desejada_titulo"),
            "curriculo_texto_extraido": dados_extracao.get("experiencia_resumo"),
            "fonte": "whatsapp",
            "updated_at": datetime.now(timezone.utc).isoformat()
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
                
                # Salva candidatura: atualiza se já existe, insere se não existe
                cand_data = {
                    "candidato_id": candidato_id,
                    "vaga_id": vaga_id,
                    "score_final": score_data.get("score", 0),
                    "justificativa_ia": score_data.get("justificativa"),
                    "pontos_fortes": score_data.get("pontos_fortes", []),
                    "pontos_atencao": score_data.get("pontos_fracos", []),
                    "status": "triagem"
                }
                existing = supabase.table("candidaturas").select("id").eq("candidato_id", candidato_id).eq("vaga_id", vaga_id).execute()
                if existing.data:
                    supabase.table("candidaturas").update(cand_data).eq("id", existing.data[0]["id"]).execute()
                    print(f"SUCESSO: Candidatura atualizada para {remetente} na vaga {vaga_titulo}")
                else:
                    supabase.table("candidaturas").insert(cand_data).execute()
                    print(f"SUCESSO: Candidatura criada para {remetente} na vaga {vaga_titulo}")
            else:
                print(f"AVISO: Vaga '{vaga_titulo}' não encontrada ou não está aberta.")

    except Exception as e:
        print(f"ERRO CRÍTICO no processamento final da candidatura: {e}")
