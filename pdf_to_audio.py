import PyPDF2
from gtts import gTTS

def read_pdf(file_path):
    pdf_reader = PyPDF2.PdfReader(file_path)
    full_text = []
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        full_text.append(page.extract_text())
    return '\n'.join(full_text)

def text_to_speech(text, language='en', output_file='101_Essays.mp3'):
    tts = gTTS(text=text, lang=language)
    tts.save(output_file)
    print(f'Audio saved as {output_file}')

if __name__ == "__main__":
    pdf_file_path = '101_Essays.pdf'  # Replace with the path to your PDF file
    text = read_pdf(pdf_file_path)
    text_to_speech(text)
