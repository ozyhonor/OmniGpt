import io
from docx import Document
import PyPDF2
import chardet
from ebooklib import epub
import ebooklib
from bs4 import BeautifulSoup


def read_epub(file_path):
    try:
        book = epub.read_epub(file_path)
        content = ""
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            content += item.get_body_content().decode('utf-8', errors='ignore')

        soup = BeautifulSoup(content, 'html.parser')
        text_content = soup.get_text()
        return text_content
    except Exception as e:
        return f'Error reading .epub file: {str(e)}'


import chardet
TYPE_TXT_FILE = None

def read_txt(file_path):

    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    encoding = result['encoding']
    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
        content = f.read()

    return content






def read_docx(file_path):
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def read_pdf(file_path):
    text = ""
    pdf = PyPDF2.PdfReader(open(file_path, 'rb'))
    for page in pdf.pages:
        text += page.extract_text()
    return text


def read_fb2(file_path):
    with open(file_path, 'rb') as file:
        data = io.BytesIO(file.read())
    text = read_txt(data)
    return text


#$def read_doc(file_path):
#$    try:
#$        word = wc.Dispatch("Word.Application")
#$        doc = word.Documents.Open(file_path)
#$        doc.SaveAs(file_path + "x", 16)
#$        text = doc.Content.Text
#$        doc.Close()
#$        word.Quit()
#$        return text
#$    except Exception as e:
#$        return str(e)


def detect_file_format(file_path):
    file_extension = file_path.split('.')[-1].lower()

    if file_extension == 'txt':
        return read_txt(file_path)
    elif file_extension == 'docx':
        return read_docx(file_path)
    elif file_extension == 'pdf':
        return read_pdf(file_path)
    elif file_extension == 'fb2':
        return read_fb2(file_path)
    elif file_extension == 'epub':
        return read_epub(file_path)
    else:
        return 'Unknown'
