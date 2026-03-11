import PyPDF2

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

if __name__ == '__main__':
    pdf_path = "Agente_IA_Selecao_Curriculos.docx (1).pdf"
    text = extract_text_from_pdf(pdf_path)
    with open('pdf_content_extracted.txt', 'w', encoding='utf-8') as out:
         out.write(text)
    print("PDF content extracted to pdf_content_extracted.txt")
