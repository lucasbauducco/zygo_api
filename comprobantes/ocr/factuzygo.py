import os
import tempfile
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from PIL import Image
import pytesseract
import cv2
from pdf2image import convert_from_path
import numpy as np
# Configuración de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
custom_oem_psm_config = r'--oem 3 --psm 3 -c tessedit_char_whitelist= + " " + ":0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz./-"'


# 1. Función para preprocesar imágenes
def preprocesar_imagen(imagen):
    """Mejora la calidad de la imagen para mejorar la extracción de texto."""
    # Convertir a escala de grises
    imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    
    # Aplicar CLAHE para mejorar el contraste
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    imagen_gris = clahe.apply(imagen_gris)

    # Eliminar ruido con suavizado
    imagen_suavizada = cv2.GaussianBlur(imagen_gris, (5, 5), 0)

    # Binarizar la imagen para separar mejor el texto del fondo
    imagen_binaria = cv2.adaptiveThreshold(imagen_suavizada, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, 11, 2)

    return imagen_binaria

# 2. Función para convertir PDF a imagen (solo la primera página)
def pdf_a_imagenes(pdf_path):
    """Convierte el archivo PDF a imágenes (solo la primera página)."""
    paginas = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=1)
    return paginas

# 3. Función para extraer texto de la imagen usando Tesseract
def extraer_texto_imagen(imagen):
    """Extrae texto de una imagen utilizando Tesseract OCR."""
    # Preprocesar la imagen antes de pasársela a Tesseract
    imagen_preprocesada = preprocesar_imagen(np.array(imagen))  # Convertir PIL a NumPy

    # Extraer texto usando Tesseract
    texto = pytesseract.image_to_string(
    imagen_preprocesada,
    config=custom_oem_psm_config,
    lang='spa'  # o 'eng+spa' si hay mezcla de inglés y español
)

    # Limpiar el texto extraído (por ejemplo, eliminar saltos de línea innecesarios)
    texto = texto.replace("\n", " ").replace("\r", "")
    texto = texto.strip()

    return texto

# 4. Función para procesar PDF y extraer texto
def extraer_texto_pdf(pdf_path):
    """Convierte el PDF a imágenes y extrae el texto de la primera página."""
    paginas = pdf_a_imagenes(pdf_path)  # Convertir el PDF a imágenes
    texto_total = ""

    # Si el PDF tiene imágenes, procesamos la primera
    if paginas:
        texto_total = extraer_texto_imagen(paginas[0])

    return texto_total

@api_view(['POST'])
def extraer_texto_factura(request):
    """Extrae texto de archivos PDF o imágenes subidas por el usuario."""
    if 'archivo' not in request.FILES:
        return Response({'error': 'No se encontró el archivo'}, status=status.HTTP_400_BAD_REQUEST)

    archivo = request.FILES['archivo']
    temp_file_path = None

    try:
        # Guardar el archivo temporalmente en el sistema
        with tempfile.NamedTemporaryFile(delete=False, suffix='.' + archivo.name.split('.')[-1]) as temp_file:
            temp_file.write(archivo.read())
            temp_file_path = temp_file.name

        # Procesar archivo PDF
        if archivo.name.lower().endswith('.pdf'):
            texto_extraido = extraer_texto_pdf(temp_file_path)
        # Procesar imágenes (JPG, JPEG, PNG, GIF)
        elif archivo.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            imagen = Image.open(temp_file_path)
            texto_extraido = extraer_texto_imagen(imagen)
        else:
            return Response({'error': 'Formato de archivo no soportado'}, status=status.HTTP_400_BAD_REQUEST)

        # Si no se extrae texto, devolver error
        if not texto_extraido.strip():
            return Response({'error': 'No se encontró texto en el archivo'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'texto': texto_extraido.strip()}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': f'Error al procesar el archivo: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)