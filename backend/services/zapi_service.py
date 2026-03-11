import os
import requests

def get_zapi_credentials():
    instance = os.getenv("ZAPI_INSTANCE", "")
    token = os.getenv("ZAPI_TOKEN", "")
    client_token = os.getenv("ZAPI_CLIENT_TOKEN", "")
    return instance, token, client_token

def enviar_mensagem_texto(telefone: str, mensagem: str):
    instance, token, client_token = get_zapi_credentials()
    if not instance or not token: return
    
    url = f"https://api.z-api.io/instances/{instance}/token/{token}/send-messages"
    headers = {"Client-Token": client_token, "Content-Type": "application/json"}
    payload = {
        "phone": telefone,
        "message": mensagem
    }
    try:
        requests.post(url, headers=headers, json=payload)
    except Exception as e:
        print(f"Erro ao enviar Z-API: {e}")

def enviar_audio(telefone: str, url_audio_publico: str):
    instance, token, client_token = get_zapi_credentials()
    if not instance or not token: return
    
    url = f"https://api.z-api.io/instances/{instance}/token/{token}/send-audio"
    headers = {"Client-Token": client_token, "Content-Type": "application/json"}
    payload = {
        "phone": telefone,
        "audio": url_audio_publico
    }
    try:
        requests.post(url, headers=headers, json=payload)
    except Exception as e:
        print(f"Erro ao enviar áudio Z-API: {e}")
