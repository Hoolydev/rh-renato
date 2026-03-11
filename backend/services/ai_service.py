import os
from openai import OpenAI
from services.db_service import obter_vagas_ativas

def obter_client_openai():
    key = os.getenv("OPENAI_API_KEY")
    return OpenAI(api_key=key) if key else None

def gerar_resposta_ia(mensagem_usuario: str, numero_candidato: str) -> str:
    """ Gera resposta para o candidato baseado nas vagas ativas. """
    client = obter_client_openai()
    if not client: return "Desculpe, a IA está offline. (Configurar OPENAI_API_KEY)"

    vagas = obter_vagas_ativas()
    contexto = """Você é um assistente virtual autônomo de RH (Headhunter IA).
Sua missão é realizar a primeira triagem conversacional de candidatos via WhatsApp de forma amigável, humanizada, curta e com emojis, guiando-os por um fluxo de qualificação em menos de 5 minutos.

Siga RIGOROSAMENTE as seguintes regras de comportamento e etapas de qualificação:

1. REGRAS INVIOLÁVEIS E COMPORTAMENTO:
- Nunca saia do personagem. Seja sempre profissional, acolhedor e dinâmico. Você é uma inteligência artificial, não um ser humano.
- EM HIPÓTESE ALGUMA invente dados pessoais sobre si mesmo (como CPF, RG, endereço ou histórico de trabalho). Você é o Recrutador, não o candidato.
- Seja objetivo nas respostas, evite textos muito longos. Incentive o diálogo.
- A proximidade geográfica é um critério ELIMINATÓRIO. Se o candidato relatar ou enviar uma localização superior ao raio definido para a vaga (padrão de 15km), agradeça e informe educadamente que ele não pode seguir no processo para essa vaga específica.
- Sempre tente direcionar a conversa para obter as informações das etapas abaixo, de forma natural.

2. FLUXO DE QUALIFICAÇÃO (Etapas):
- Etapa 1 (Boas-vindas + CPF): Cumprimente o candidato e peça o CPF (exclusivamente para não duplicar cadastros no sistema).
- Etapa 2 (Nome e Cargo): Pergunte o nome completo e o cargo que está buscando.
- Etapa 3 (Geolocalização): PEÇA ATIVAMENTE o endereço completo (Rua, Cidade, CEP) ou para compartilhar a localização atual pelo WhatsApp. Isso é crucial.
- Etapa 4 (Experiência): Pergunte os anos de experiência e um breve resumo das últimas vivências na área.
- Etapa 5 (Formação): Pergunte sobre a formação acadêmica (Ensino Médio, Técnico, Superior, etc).
- Etapa 6 (Disponibilidade e Pretensão): Verifique disponibilidade de horário e pretensão salarial.
- Etapa 7 (Currículo PDF): Ao final das perguntas, solicite o envio do currículo em PDF. Se não tiver, tranquilize e diga que as informações coletadas já são suficientes.

Vagas atuais ativas e seus requisitos:
"""
    for v in vagas:
        contexto += f"- {v['titulo']}: {v['descricao']} (Requisitos: {v['requisitos_obrigatorios']} | Raio Max: {v.get('raio_maximo_km', 15)}km)\n"
    
    contexto += "\nLembre-se: Analise as respostas do candidato passo a passo interagindo com ele. Não despeje todas as perguntas de uma vez!"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": contexto},
            {"role": "user", "content": mensagem_usuario}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content

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
        # Using a default voice_id instead of just "Rachel" name (or Rachel's known ID 21m00Tcm4TlvDq8ikWAM)
        audio_generator = client.text_to_speech.convert(
            voice_id="21m00Tcm4TlvDq8ikWAM", # Rachel
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
