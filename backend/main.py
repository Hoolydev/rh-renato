import os
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from services.db_service import criar_vaga, salvar_configuracoes, obter_vagas_ativas, supabase
from services.ai_service import gerar_resposta_ia
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
    
    # Exemplo genérico de como receber mensagem Z-API
    # Verifica se a mensagem de texto chegou
    if "isGroup" in payload and not payload["isGroup"]:
        texto_recebido = payload.get("text", {}).get("message", "")
        remetente = payload.get("phone", "")
        
        if texto_recebido:
            # Fluxo de WhatsApp Inteligente (Candidato enviando mensagem para a vaga)
            # 1. Simular Lead Scoring Rápido caso detecte que é um envio de perfil:
            if "currículo" in texto_recebido.lower() or "experiência" in texto_recebido.lower():
                score = calcular_lead_scoring(
                    texto_curriculo=texto_recebido,
                    titulo_vaga="Vaga Genérica",
                    descricao_vaga="Analisar experiência",
                    requisitos_vaga="Qualquer perfil válido"
                )
                resposta_texto = f"IA analisou seu perfil do WhatsApp! Lead Score gerado: {score['score']}/100. Pontos fortes: {', '.join(score['pontos_fortes'])}."
            else:
                # 2. Resposta IA normal de RH
                resposta_texto = gerar_resposta_ia(texto_recebido, remetente)
            
            # 3. Enviar no Zap
            enviar_mensagem_texto(remetente, resposta_texto)
            
    return {"status": "received"}

@app.get("/api/verificar_emails")
async def endpoint_verificar_emails():
    # Rota para disparar manualmente ou agendada
    total_baixados = verificar_novos_curriculos()
    return {"novos_curriculos": total_baixados}
