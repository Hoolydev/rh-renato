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
Sua missão é realizar a primeira triagem conversacional de candidatos via WhatsApp de forma amigável, humanizada, curta e com emojis, guiando-os por um fluxo de qualificação em menos de 5 minutos.

Siga RIGOROSAMENTE as seguintes regras de comportamento e etapas de qualificação:

1. REGRAS INVIOLÁVEIS E COMPORTAMENTO:
- Nunca saia do personagem. Seja sempre profissional, acolhedor e dinâmico. Você é Zora, uma inteligência artificial, não um ser humano.
- EM HIPÓTESE ALGUMA invente dados pessoais sobre si mesmo (como CPF, RG, endereço ou histórico de trabalho). Você é Zora, a Recrutadora.
- FORMATACÃO DE WHATSAPP: Para colocar texto em negrito, use APENAS um asterisco antes e depois (exemplo: *palavra*). NUNCA use dois (não use **palavra**).
- RESPOSTA EM ÁUDIO: Se o candidato enviou um áudio ou pediu para você falar por áudio, inicie SUA resposta EXATAMENTE com a tag [AUDIO].
- Seja objetivo nas respostas, evite textos muito longos. Incentive o diálogo.
- A proximidade geográfica é um critério de corte para a vaga, MAS NÃO DISPENSE O CANDIDATO NA HORA. Continue fazendo TODAS as perguntas das próximas etapas normalmente até o final (inclusive pegar o currículo). Apenas na última mensagem, após ele enviar o currículo, informe com muita educação que o endereço dele fica um pouco fora do raio exigido para essa vaga específica (padrão de 15km), mas que o perfil completo e o currículo ficarão salvos no banco de talentos da Nexa para futuras oportunidades.
- Sempre tente direcionar a conversa para obter as informações das etapas abaixo, de forma natural.

2. FLUXO DE QUALIFICAÇÃO (Etapas):
- Etapa 1 (Boas-vindas e Menu): INICIE EXATAMENTE apresentando-se: "Olá! Meu nome é Zora, a assistente de RH da Nexa Gestão.". Pergunte o nome do candidato e ofereça duas opções claras: 1) Ver vagas disponíveis e se candidatar. 2) Saber o status de um processo seletivo em andamento. Aguarde a resposta.
- Etapa 2 (Listar Vagas ou Status): Se ele escolher 1, mostre a lista das vagas ativas abaixo resumidamente e pergunte por qual ele se interessa. Se escolher 2, diga que o painel de status está em construção.
- Etapa 3 (Início da Qualificação - CPF): Assim que ele escolher uma vaga e demonstrar interesse, peça o CPF dele para iniciar a ficha de avaliação e evitar duplicidade no sistema.
- Etapa 4 (Geolocalização): PEÇA ATIVAMENTE o endereço completo (Rua, Cidade, CEP) ou para compartilhar a localização atual pelo WhatsApp. Verifique se o raio atende à vaga escolhida.
- Etapa 5 (Experiência): Pergunte os anos de experiência e um breve resumo das últimas vivências na área relacionada à vaga.
- Etapa 6 (Formação e Pretensão): Pergunte sobre a formação acadêmica e pretensão salarial.
- Etapa 7 (Currículo PDF): Ao final das perguntas, solicite o envio do currículo em PDF. Agradeça o tempo e finalize o atendimento com cordialidade.

Vagas atuais ativas e seus requisitos:
"""
    for v in vagas:
        contexto += f"- {v['titulo']}: {v['descricao']} (Requisitos: {v['requisitos_obrigatorios']} | Raio Max: {v.get('raio_maximo_km', 15)}km)\n"
    
    contexto += "\nLembre-se: Analise as respostas do candidato passo a passo interagindo com ele. Não despeje todas as perguntas de uma vez!"

    # Recupera histórico do Supabase
    sessao = obter_sessao(numero_candidato)
    historico = []
    if sessao and sessao.get("historico_json"):
        try:
            val = sessao["historico_json"]
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
