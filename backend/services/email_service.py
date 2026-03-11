import os
import imaplib
import email
from email.header import decode_header
import PyPDF2
from io import BytesIO

from services.ai_service import analisar_pdf_curriculo
from services.db_service import salvar_candidato

def verificar_novos_curriculos():
    """ 
    Acessa o Gmail via IMAP para ler e-mails não lidos, 
    extrair anexos PDF e processar via IA.
    """
    user = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")
    
    if not user or not password:
        print("Credenciais do Gmail não configuradas.")
        return 0

    try:
        # Conectar ao servidor IMAP do Gmail
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, password)
        mail.select("inbox")

        # Buscar e-mails não lidos
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            return 0

        email_ids = messages[0].split()
        processados = 0

        for email_id in email_ids:
            _, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Obter Assunto e Remetente
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    remetente = msg.get("From")

                    # Processar anexos do e-mail
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_disposition = str(part.get("Content-Disposition"))
                            if "attachment" in content_disposition:
                                filename = part.get_filename()
                                if filename and filename.lower().endswith(".pdf"):
                                    pdf_bytes = part.get_payload(decode=True)
                                    texto_pdf = extrair_texto_pdf(pdf_bytes)
                                    
                                    # Analisar com GPT
                                    json_dados = analisar_pdf_curriculo(texto_pdf)
                                    # Salvar no DB
                                    # A conversão de json para dict seria aqui (json.loads)
                                    # salvar_candidato(json_dados_dict)
                                    
                                    processados += 1

            # Opcional: Marcar como lido (descomentar)
            # mail.store(email_id, '+FLAGS', '\\Seen')

        mail.logout()
        return processados
    except Exception as e:
        print(f"Erro ao acessar Gmail: {e}")
        return 0

def extrair_texto_pdf(pdf_bytes):
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        texto = ""
        for page in pdf_reader.pages:
            texto += page.extract_text() or ""
        return texto
    except Exception as e:
        print("Erro lendo PDF:", e)
        return ""
