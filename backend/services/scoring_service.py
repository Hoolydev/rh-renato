import os
import json
from openai import OpenAI

def obter_client_openai():
    key = os.getenv("OPENAI_API_KEY")
    return OpenAI(api_key=key) if key else None

def calcular_lead_scoring(texto_curriculo: str, titulo_vaga: str, descricao_vaga: str, requisitos_vaga: str) -> dict:
    """
    Analisa o currículo frente à vaga e retorna uma pontuação e justificativa.
    """
    client = obter_client_openai()
    if not client:
        # Mock para ambientes sem API KEY
        return {
            "score": 87,
            "justificativa": "O candidato possui a maioria dos requisitos, mas falta experiência específica na ferramenta avançada exigida.",
            "pontos_fortes": ["Experiência prévia sólida", "Boa comunicação escrita", "Formação adequada"],
            "pontos_fracos": ["Falta a ferramenta principal avançada"]
        }
        
    prompt = f"""
    Você é um especialista em Recrutamento e Seleção (Headhunter) com habilidade em Lead Scoring de currículos.
    Sua tarefa é fazer o Lead Scoring (0 a 100) do candidato para a vaga abaixo comparando as informações.
    
    VAGA: {titulo_vaga}
    DESCRIÇÃO: {descricao_vaga}
    REQUISITOS OBRIGATÓRIOS: {requisitos_vaga}
    
    CURRÍCULO DO CANDIDATO:
    {texto_curriculo}
    
    Retorne a análise ESTRITAMENTE em formato JSON puro, sem usar blocos de código com crases markdown, usando a estrutura:
    {{
      "score": (número inteiro de 0 a 100 indicando a aderência/fit),
      "justificativa": "(breve resumo do porquê dessa nota)",
      "pontos_fortes": ["(lista de strings - o que se destacou?)"],
      "pontos_fracos": ["(lista de strings - o que faltou?)"]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        conteudo = response.choices[0].message.content.strip()
        # Tratamento simples caso o LLM insista em retornar markdowns
        if conteudo.startswith("```json"):
            conteudo = conteudo.replace("```json", "", 1)
        if conteudo.endswith("```"):
            conteudo = conteudo[:-3]
            
        return json.loads(conteudo.strip())
    except Exception as e:
        print(f"Erro no Lead Scoring: {e}")
        return {"score": 0, "justificativa": f"Erro na análise via LLM: {str(e)}", "pontos_fortes": [], "pontos_fracos": []}
