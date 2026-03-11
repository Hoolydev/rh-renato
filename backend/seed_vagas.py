import os
import json
from dotenv import load_dotenv

# Explicitly load from backend/.env when running from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from services.db_service import criar_vaga

MOCK_VAGAS = [
    {
        "titulo": "Porteiro / Controlador",
        "descricao": "Controle de acesso em portaria de condomínio, ronda perimetral e atendimento aos moradores.",
        "empresa": "Condomínio Residencial",
        "responsavel_email": "admin@empresa.com",
        "endereco_sede": "Centro, São Paulo/SP",
        "latitude_sede": -23.55052,
        "longitude_sede": -46.633308,
        "raio_maximo_km": 15,
        "requisitos_obrigatorios": json.dumps(["Ensino Médio completo", "Curso de Portaria atualizado"]),
        "requisitos_desejados": json.dumps(["Experiência prévia em condomínio residencial"]),
        "salario_min": 1800,
        "salario_max": 2000,
        "regime": "CLT",
        "status": "aberta"
    },
    {
        "titulo": "Vigilante Patrimonial",
        "descricao": "Vigilância armada para agência bancária. Realizar escolta interna e proteção do patrimônio.",
        "empresa": "Banco Nacional",
        "responsavel_email": "admin@empresa.com",
        "endereco_sede": "Pinheiros, São Paulo/SP",
        "latitude_sede": -23.56515,
        "longitude_sede": -46.69680,
        "raio_maximo_km": 20,
        "requisitos_obrigatorios": json.dumps(["Curso de Vigilante (CNV) em dia", "Reciclagem armada atualizada"]),
        "requisitos_desejados": json.dumps(["CNH B", "Experiência em banco"]),
        "salario_min": 3000,
        "salario_max": 3500,
        "regime": "CLT",
        "status": "aberta"
    },
    {
        "titulo": "Auxiliar de Limpeza",
        "descricao": "Atividades de higienização e conservação de consultórios médicos e recepção.",
        "empresa": "Clínica Médica",
        "responsavel_email": "admin@empresa.com",
        "endereco_sede": "Vila Mariana, São Paulo/SP",
        "latitude_sede": -23.589832,
        "longitude_sede": -46.634170,
        "raio_maximo_km": 10,
        "requisitos_obrigatorios": json.dumps(["Experiência mínima de 6 meses em limpeza hospitalar ou clínica"]),
        "requisitos_desejados": json.dumps(["Fácil acesso ao metrô"]),
        "salario_min": 1500,
        "salario_max": 1800,
        "regime": "CLT",
        "status": "aberta"
    }
]

def run_seed():
    print("Iniciando seed de vagas mockadas...")
    for vaga in MOCK_VAGAS:
        try:
            vaga_id = criar_vaga(vaga)
            if vaga_id:
                print(f"Vaga '{vaga['titulo']}' criada com ID: {vaga_id}")
            else:
                print(f"Erro ao criar a vaga '{vaga['titulo']}'")
        except Exception as e:
            print(f"Erro ao inserir {vaga['titulo']}: {e}")
    print("Seed finalizado.")

if __name__ == "__main__":
    run_seed()
