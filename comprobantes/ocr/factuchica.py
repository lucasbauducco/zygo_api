import pytesseract
from pdf2image import convert_from_path
import sys

# Asegúrate de que pytesseract está apuntando a la ruta correcta de Tesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Ajusta la ruta si es necesario

def extraer_texto_pdf(archivo_pdf):
    # Convierte las páginas del archivo PDF a imágenes
    paginas = convert_from_path(archivo_pdf, 300)  # Ajusta el DPI si es necesario
    
    texto_completo = ""

    for num_pagina, imagen in enumerate(paginas):
        # Extrae el texto de la imagen usando OCR (pytesseract)
        texto_extraido = pytesseract.image_to_string(imagen, config='--psm 6', lang='spa')
        texto_completo += f"\n--- Página {num_pagina + 1} ---\n"
        texto_completo += texto_extraido.strip()
        texto_completo += "\n\n"  # Agrega un salto de línea después del texto de cada página
    
    return texto_completo

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python extraer_texto_pdf.py <archivo_pdf>")
    else:
        archivo_pdf = sys.argv[1]
        
        # Extrae el texto del PDF
        texto = extraer_texto_pdf(archivo_pdf)
        
        # Imprime el texto extraído
        print(texto)