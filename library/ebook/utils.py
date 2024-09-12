import PyPDF2

def calculate_pages(content_file):
    if content_file:
        try:
            with content_file.open('rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                return num_pages
        except PyPDF2.errors:
            return None
    else:
        return None
    
def extract_text_from_pdf(content_file):
    text = ""
    with content_file.open("rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text