import os
from openai import OpenAI
from services.db_service import obter_vagas_ativas

historico_conversas = {}

def obter_client_openai():
    key = os.getenv("OPENAI_API_KEY")
    return OpenAI(api_key=key) if key else None

def gerar_resposta_ia(mensagem_usuario: str, numero_candidato: str) -> str:
    """ Gera resposta para o candidato baseado nas vagas ativas e persiste histórico. """
    from services.db_service import obter_vagas_ativas, obter_sessao, salvar_sessao
    import json

    client = obter_client_openai()
    if not client: return "Desculpe, a IA está offline. (Configurar OPENAI_API_KEY)"

    vagas = obter_vagas_ativas()
    contexto = """Você é Zora, uma assistente virtual autônoma de RH (Headhunter IA).
Sua missão é realizar a primeira triagem conversacional de candidatos via WhatsApp de forma amigável, humanizada, curta e com emojis.

Siga RIGOROSAMENTE as seguintes regras de comportamento e etapas de qualificação:

1. REGRAS INVIOLÁVEIS E COMPORTAMENTO:
- Nunca saia do personagem. Você é Zora, a Recrutadora.
- FORMATACÃO DE WHATSAPP: Para colocar texto em negrito, use APENAS um asterisco antes e depois (exemplo: *palavra*). NUNCA use dois.
- RESPOSTA EM ÁUDIO: Se o candidato enviou um áudio, inicie SUA resposta EXATAMENTE com a tag [AUDIO].
- PERTINÊNCIA: Suas perguntas devem ser objetivas.
- EXPERIÊNCIA: Se as informações sobre a experiência profissional não estiverem claras (mesmo após o envio do currículo), faça perguntas específicas sobre o que ele já fez na área da vaga.
- DISCRIÇÃO ABSOLUTA: JAMAIS mencione score, pontuação, nota, avaliação numérica, porcentagem de fit, ranking ou qualquer dado interno de análise ao candidato. Esses dados são EXCLUSIVAMENTE internos da plataforma. Se perguntado sobre sua nota ou avaliação, responda apenas: "Não compartilho detalhes do processo de análise, mas em breve você receberá um retorno da nossa equipe. 😊"

2. FLUXO DE QUALIFICAÇÃO (Etapas):
- Etapa 1 (Início): Apresente-se ("Olá! Meu nome é Zora, a assistente de RH da Nexa Gestão. 😊") e pergunte o *nome completo*. Ofereça as vagas disponíveis.
- Etapa 2 (Vaga): Assim que ele escolher a vaga, peça o *CPF* (apenas números) para o cadastro.
- Etapa 3 (Localização): Peça o *CEP* ou endereço completo para validar a distância da sede.
- Etapa 4 (Experiência e Currículo): Peça o currículo em *PDF*. 
    - Se após analisar o currículo (ou se ele não tiver) a experiência não estiver clara, pergunte sobre o tempo de atuação e atividades principais na área.
- Etapa 5 (Finalização): Quando tiver todas as informações básicas (Nome, CPF, CEP, Experiência e Currículo), encerre a conversa.
    - Sua ÚLTIMA MENSAGEM deve ser exatamente: "Vamos analisar seu currículo e em breve daremos retorno. 😊" seguida obrigatoriamente da tag oculta [FIM_ENTREVISTA].

Vagas atuais ativas:
"""
    for v in vagas:
        contexto += f"- {v['titulo']}: {v['descricao']} (Requisitos: {v['requisitos_obrigatorios']} | Raio Max: {v.get('raio_maximo_km', 15)}km)\n"
    
    contexto += "\nLembre-se: Analise as respostas do candidato passo a passo interagindo com ele. Não despeje todas as perguntas de uma vez!"

    # Recupera histórico do Supabase
    sessao = obter_sessao(numero_candidato)
    historico = []
    if sessao and sessao.get("dados_candidato"):
        try:
            dados = sessao["dados_candidato"]
            if isinstance(dados, str):
                dados = json.loads(dados)
            val = dados.get("historico_ia")
            if val:
                historico = json.loads(val) if isinstance(val, str) else val
        except:
            historico = []

    # Inicializa ou atualiza o System Prompt no topo
    if not historico:
        historico.append({"role": "system", "content": contexto})
    else:
        historico[0] = {"role": "system", "content": contexto}
    
    historico.append({"role": "user", "content": mensagem_usuario})

    # Limite de contexto (System + últimas 19 mensagens)
    historico_para_ia = [historico[0]] + historico[-19:]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=historico_para_ia,
            max_tokens=400
        )
        resposta = response.choices[0].message.content
        
        # Adiciona resposta ao histórico e salva no banco
        historico.append({"role": "assistant", "content": resposta})
        
        # Mantém apenas as últimas 20 mensagens no histórico salvo para sanidade do DB
        if len(historico) > 21:
            historico = [historico[0]] + historico[-20:]
            
        salvar_sessao(numero_candidato, historico)
        return resposta
    except Exception as e:
        print(f"Erro OpenAI: {e}")
        return "Desculpe, tive um probleminha técnico. Pode repetir?"

def analisar_pdf_curriculo(texto_pdf):
    client = obter_client_openai()
    if not client: return "{}"

    prompt = f"Dado o seguinte currículo:\n\n{texto_pdf}\n\nExtraia os seguintes campos em JSON puro (sem markdown): nome, email, telefone, cargo_desejado, anos_experiencia (inteiro)."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    return response.choices[0].message.content

def gerar_audio_ia(texto: str, nome_arquivo_saida="response.ogg"):
    """ Usa ElevenLabs para gerar áudio baseado no texto da IA """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key: return ""
    from elevenlabs.client import ElevenLabs
    
    try:
        client = ElevenLabs(api_key=api_key)
        
        audio_generator = client.text_to_speech.convert(
            voice_id="33B4UnXyTNbgLmdEDh5P", # Zora Custom Voice
            output_format="mp3_44100_128",
            text=texto,
            model_id="eleven_multilingual_v2"
        )
        
        with open(nome_arquivo_saida, "wb") as f:
            for chunk in audio_generator:
                if chunk:
                    f.write(chunk)
                    
        return nome_arquivo_saida
    except Exception as e:
        print("Erro ElevenLabs:", e)
        return ""

def transcrever_audio_zapi(audio_url: str) -> str:
    import requests
    import os
    client = obter_client_openai()
    if not client: return ""
    
    try:
        resposta = requests.get(audio_url)
        # Usa o diretório /tmp que é gravável na Vercel
        temp_file = "/tmp/temp_audio_in.ogg"
        with open(temp_file, "wb") as f:
            f.write(resposta.content)
            
        with open(temp_file, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=f
            )
        os.remove(temp_file)
        return transcript.text
    except Exception as e:
        print("Erro Whisper Transcrição:", e)
        return ""
