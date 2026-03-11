import sys
from PyPDF2 import PdfReader

try:
    reader = PdfReader('Agente_IA_Selecao_Curriculos.docx (1).pdf')
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    print("--- CONTENT START ---")
    print(text[:2000]) # First 2000 chars to review
    print("--- CONTENT END ---")
except Exception as e:
    print(f"Error: {e}")
