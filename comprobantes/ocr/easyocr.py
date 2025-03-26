import os
import tempfile
import cv2
import numpy as np
import pdfplumber
from PIL import Image
from pdf2image import convert_from_path
import easyocr
import numpy as np
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import pytesseract
# Inicializar el lector de EasyOCR para inglés y español
reader = easyocr.Reader(['en', 'es'])
custom_config = r'--oem 3 --psm 6'
# Configurar Tesseract (ruta en Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# -----------------------------------------------------------------------------------
# 1. Función para corrección de orientación (deskew)
# -----------------------------------------------------------------------------------
def deskew(imagen_gris):
    coords = np.column_stack(np.where(imagen_gris > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = imagen_gris.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(imagen_gris, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

def mejorar_contraste(imagen_gris):
    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
    return clahe.apply(imagen_gris)
def detectar_bordes(imagen_gris):
    bordes = cv2.Canny(imagen_gris, threshold1=30, threshold2=100)
    return bordes
def reducir_ruido(imagen_gris):
    return cv2.bilateralFilter(imagen_gris, d=5, sigmaColor=100, sigmaSpace=5)
    return imagen_suavizada
def detectar_lineas(imagen_gris):
    edges = cv2.Canny(imagen_gris, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
    return lines
def binarizar_imagen(imagen_gris):
    _, otsu = cv2.threshold(imagen_gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    adaptive = cv2.adaptiveThreshold(imagen_gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return cv2.bitwise_or(otsu, adaptive)

    return imagen_binaria
def aumentar_resolucion(imagen):
    imagen_res = cv2.resize(imagen, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return imagen_res
def limpiar_imagen(imagen_binaria):
    kernel = np.ones((3, 3), np.uint8)
    imagen_limpia = cv2.morphologyEx(imagen_binaria, cv2.MORPH_CLOSE, kernel)
    return imagen_limpia
# -----------------------------------------------------------------------------------
# 2. Función para preprocesar imágenes
# -----------------------------------------------------------------------------------
def preprocesar_imagen_mejorado(imagen_bgr):
    """
    Preprocesa la imagen aplicando técnicas avanzadas de mejora:
    - Aumento de contraste
    - Reducción de ruido
    - Detección de bordes y líneas
    - Binarización avanzada
    """
    imagen_gris = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2GRAY)

    # Mejorar el contraste
    imagen_contraste = mejorar_contraste(imagen_gris)

    # Reducir ruido
    imagen_suavizada = reducir_ruido(imagen_contraste)

    # Binarización avanzada
    #imagen_binaria = binarizar_imagen(imagen_gris)

    # Opcional: Corrección de orientación si es necesario
    imagen_enderezada = imagen_suavizada

    return imagen_enderezada
def preprocesar_imagen(imagen_bgr):

    return imagen_bgr


def realizar_ocr(imagen):
    """
    Realiza OCR en una imagen dada y devuelve el texto extraído.
    (Se debe integrar con Tesseract o EasyOCR en tu código principal)
    """
    return pytesseract.image_to_string(imagen, lang="spa+eng").strip()
# -----------------------------------------------------------------------------------
# 3. Función para convertir PDF a imagen (solo la primera página)
# -----------------------------------------------------------------------------------
def pdf_a_imagenes(pdf_path):
    paginas = convert_from_path(pdf_path, dpi=600, first_page=1, last_page=1)
    return paginas


# -----------------------------------------------------------------------------------
# 4. Función para extraer texto de la imagen usando EasyOCR
# -----------------------------------------------------------------------------------
def extraer_texto_imagen(imagen_pil):
    """
    Extrae texto de una imagen usando primero EasyOCR.
    Si EasyOCR falla, usa Tesseract como fallback.
    """
    imagen_np = np.array(imagen_pil)
    imagen_preprocesada = preprocesar_imagen_mejorado(imagen_np)

    # Intentar OCR con EasyOCR
    resultado_easyocr = reader.readtext(imagen_preprocesada, detail=0)
    texto_easyocr = ' '.join(resultado_easyocr).strip()

    # Si EasyOCR no extrajo texto válido, probar con Tesseract
    if not texto_easyocr or len(texto_easyocr) < 5:
        texto_tesseract = realizar_ocr(imagen_preprocesada)
        return texto_tesseract.strip()

    return texto_easyocr

# -----------------------------------------------------------------------------------
# 5. Función para extraer texto de un PDF usando pdfplumber (texto nativo)
# -----------------------------------------------------------------------------------
def extraer_texto_pdf_plumber(pdf_path):
    """
    Intenta extraer el texto directamente (si el PDF no está escaneado).
    Retorna el texto extraído o cadena vacía si no encuentra nada.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) > 0:
                # Extraer texto de la primera página
                page = pdf.pages[0]
                text = page.extract_text()
                if text:
                    return text
    except Exception:
        # En caso de error, retorna vacío
        pass
    return ""

# -----------------------------------------------------------------------------------
# 6. Función para extraer texto de PDF (combinando pdfplumber y OCR)
# -----------------------------------------------------------------------------------
def extraer_texto_pdf(pdf_path):
    """
    Primero intenta extraer texto nativo con pdfplumber.
    Si no encuentra nada, asume que es un PDF escaneado y recurre a OCR.
    """
    # 6.1 Intentar extraer con pdfplumber
    texto_plumber = extraer_texto_pdf_plumber(pdf_path)
    if texto_plumber.strip():
        return texto_plumber

    # 6.2 Fallback: convertir la primera página a imagen y usar OCR
    paginas = pdf_a_imagenes(pdf_path)
    if paginas:
        return extraer_texto_imagen(paginas[0])
    
    # Si no hay páginas o no se pudo extraer nada
    return ""
