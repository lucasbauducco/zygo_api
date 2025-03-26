"""
pytesseract
pip install pytesseract
pdfimage
pip install pdf2image
instalar Tesseract-OCR
"""
import pytesseract
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from io import BytesIO
import sys

def proteger_pdf_y_extraer_texto(archivo_original, archivo_protegido, clave):
    # Convierte las páginas del archivo PDF a imágenes
    paginas = convert_from_path(archivo_original)
    
    # Crea un objeto PdfWriter para construir el nuevo PDF protegido
    pdf_protegido = PdfWriter()

    for num_pagina, imagen in enumerate(paginas):
        # Extrae el texto de la imagen usando OCR (pytesseract)
        texto_extraido = pytesseract.image_to_string(imagen)
        print("Texto extraído de la página {}:".format(num_pagina + 1))
        print(texto_extraido)
        
        # Convierte la imagen a PDF en bytes
        imagen_en_bytes = BytesIO()
        imagen.save(imagen_en_bytes, format='PDF')
        imagen_en_bytes.seek(0)
        
        # Lee la imagen convertida como un PDF
        imagen_como_pdf = PdfReader(imagen_en_bytes)
        
        # Agrega la página al nuevo PDF
        pdf_protegido.add_page(imagen_como_pdf.pages[0])

    # Protege el PDF con la contraseña
    pdf_protegido.encrypt(clave)
    
    # Guarda el PDF protegido
    with open(archivo_protegido, 'wb') as archivo:
        pdf_protegido.write(archivo)
        print(f"PDF protegido guardado como: {archivo_protegido}")

# Verifica si los argumentos son correctos
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python facturita1.py <archivo_original> <archivo_protegido> <clave>")
    else:
        archivo_original = sys.argv[1]
        archivo_protegido = sys.argv[2]
        clave = sys.argv[3]
        
        # Llama a la función
        proteger_pdf_y_extraer_texto(archivo_original, archivo_protegido, clave)