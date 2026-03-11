import os
from supabase import create_client, Client

url: str = os.getenv("SUPABASE_URL", "")
key: str = os.getenv("SUPABASE_KEY", "")

supabase: Client = create_client(url, key) if url and key else None

def criar_vaga(dados_vaga):
    if not supabase: return "no_db"
    res = supabase.table("vagas").insert(dados_vaga).execute()
    return res.data[0]["id"] if res.data else None

def obter_vagas_ativas():
    if not supabase: return []
    res = supabase.table("vagas").select("*").eq("status", "aberta").execute()
    return res.data

def salvar_configuracoes(email, whatsapp):
    # Salvando no localStorage por ora ou em uma tabela específica (mock para MVP)
    pass

def salvar_candidato(dados):
    if not supabase: return None
    res = supabase.table("candidatos").insert(dados).execute()
    return res.data[0]["id"] if res.data else None

def atualizar_candidato(candidato_id, dados):
    if not supabase: return
    supabase.table("candidatos").update(dados).eq("id", candidato_id).execute()

def obter_sessao(telefone):
    if not supabase: return None
    res = supabase.table("sessoes_whatsapp").select("*").eq("numero_whatsapp", telefone).execute()
    return res.data[0] if res.data else None

def salvar_sessao(telefone, historico):
    if not supabase: return
    # Verifica se já existe sessao
    sessao = obter_sessao(telefone)
    dados = {
        "numero_whatsapp": telefone,
        "historico_json": historico
    }
    if sessao:
        supabase.table("sessoes_whatsapp").update(dados).eq("numero_whatsapp", telefone).execute()
    else:
        supabase.table("sessoes_whatsapp").insert(dados).execute()
