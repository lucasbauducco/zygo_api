import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import cv2
import numpy as np
import tempfile
import os
import re

# Configuración de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
custom_oem_psm_config = r'--oem 3 --psm 11 -c tessedit_char_whitelist="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz./-"'

def limpiar_texto(texto):
    """Corrige fechas mal detectadas y limpia caracteres no deseados."""
    texto = re.sub(r'(\d{2})[^\d](\d{2})[^\d](\d{4})', r'\1/\2/\3', texto)  # 15 07 2024 → 15/07/2024
    texto = re.sub(r'[^\w\s.,:/-]', '', texto)  # Elimina caracteres extraños
    texto = re.sub(r'\s+', ' ', texto).strip()  # Normaliza espacios
    return texto

def preprocesar_imagen_opencv(imagen_path):
    """Preprocesa la imagen para mejorar el OCR."""
    imagen = cv2.imread(imagen_path, cv2.IMREAD_GRAYSCALE)

    # Aumentar contraste con CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    imagen = clahe.apply(imagen)

    # Eliminar ruido y mejorar bordes
    imagen = cv2.GaussianBlur(imagen, (3, 3), 0)
    imagen = cv2.adaptiveThreshold(imagen, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Aumentar nitidez
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    imagen = cv2.filter2D(imagen, -1, kernel)

    # Guardar imagen temporalmente
    temp_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    cv2.imwrite(temp_filename, imagen)
    return temp_filename

def extraer_texto_pdf(archivo_pdf):
    """Convierte PDF a imagen y extrae texto con OCR."""
    paginas = convert_from_path(archivo_pdf, dpi=300, first_page=1, last_page=1)  # DPI óptimo sin perder calidad
    temp_img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    paginas[0].save(temp_img_path, 'PNG')

    imagen_procesada = preprocesar_imagen_opencv(temp_img_path)
    texto_extraido = pytesseract.image_to_string(imagen_procesada, config=custom_oem_psm_config)

    # Limpieza de archivos temporales
    for archivo in [imagen_procesada, temp_img_path]:
        try:
            os.remove(archivo)
        except FileNotFoundError:
            pass

    return limpiar_texto(texto_extraido)

def extraer_texto_imagen(archivo_imagen):
    """Extrae texto de imágenes usando OCR."""
    imagen_procesada = preprocesar_imagen_opencv(archivo_imagen)
    texto = pytesseract.image_to_string(imagen_procesada, config=custom_oem_psm_config)

    # Limpieza de archivos temporales
    try:
        os.remove(imagen_procesada)
    except FileNotFoundError:
        pass

    return limpiar_texto(texto)