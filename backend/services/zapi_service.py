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

def enviar_audio(telefone: str, path_or_url: str):
    import base64
    instance, token, client_token = get_zapi_credentials()
    if not instance or not token: return
    
    url = f"https://api.z-api.io/instances/{instance}/token/{token}/send-audio"
    headers = {"Client-Token": client_token, "Content-Type": "application/json"}
    
    # Se for um arquivo local criado pelo ElevenLabs (termos em .ogg ou .mp3)
    if os.path.isfile(path_or_url):
        with open(path_or_url, "rb") as audio_file:
            encoded_string = base64.b64encode(audio_file.read()).decode("utf-8")
        audio_content = f"data:audio/mp3;base64,{encoded_string}"
    else:
        audio_content = path_or_url

    payload = {
        "phone": telefone,
        "audio": audio_content
    }
    try:
        requests.post(url, headers=headers, json=payload)
    except Exception as e:
        print(f"Erro ao enviar áudio Z-API: {e}")
