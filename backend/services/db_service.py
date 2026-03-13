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
    res = supabase.table("sessoes_whatsapp").select("*").eq("phone", telefone).execute()
    return res.data[0] if res.data else None

def limpar_sessao(telefone):
    if not supabase: return
    supabase.table("sessoes_whatsapp").delete().eq("phone", telefone).execute()

def mensagem_ja_processada(telefone: str, message_id: str) -> bool:
    """Verifica se um messageId já foi processado. Persiste no Supabase (funciona em serverless)."""
    if not supabase or not message_id: return False
    sessao = obter_sessao(telefone)
    if not sessao: return False
    import json
    dados = sessao.get("dados_candidato") or {}
    if isinstance(dados, str):
        try: dados = json.loads(dados)
        except: dados = {}
    return message_id in dados.get("msgs_processadas", [])

def marcar_mensagem_processada(telefone: str, message_id: str):
    """Registra um messageId como processado na sessão do candidato."""
    if not supabase or not message_id: return
    sessao = obter_sessao(telefone)
    import json
    dados = {}
    if sessao:
        dados = sessao.get("dados_candidato") or {}
        if isinstance(dados, str):
            try: dados = json.loads(dados)
            except: dados = {}
    msgs = dados.get("msgs_processadas", [])
    if message_id not in msgs:
        msgs = msgs[-19:] + [message_id]   # mantém no máximo 20 IDs
        dados["msgs_processadas"] = msgs
        if sessao:
            supabase.table("sessoes_whatsapp").update({"dados_candidato": dados}).eq("phone", telefone).execute()
        else:
            supabase.table("sessoes_whatsapp").insert({"phone": telefone, "dados_candidato": dados}).execute()

def salvar_sessao(telefone, historico):
    if not supabase: return
    # Verifica se já existe sessao
    sessao = obter_sessao(telefone)
    
    if sessao:
        dados_atuais = sessao.get("dados_candidato") or {}
        import json
        if isinstance(dados_atuais, str):
            try: dados_atuais = json.loads(dados_atuais)
            except: dados_atuais = {}
        dados_atuais["historico_ia"] = historico
        supabase.table("sessoes_whatsapp").update({"dados_candidato": dados_atuais}).eq("phone", telefone).execute()
    else:
        supabase.table("sessoes_whatsapp").insert({
            "phone": telefone,
            "dados_candidato": {"historico_ia": historico}
        }).execute()
