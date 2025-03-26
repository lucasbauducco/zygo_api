import os
import tempfile
import cv2
import numpy as np
import pdfplumber
from PIL import Image
from pdf2image import convert_from_path
import easyocr
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import pytesseract
# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# Inicializar el lector de EasyOCR para inglés y español
reader = easyocr.Reader(['en', 'es'])
custom_config = r'--oem 3 --psm 6'
# Configurar Tesseract (ruta en Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# -----------------------------------------------------------------------------------
# 1. Corrección de orientación (Deskew)
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

# -----------------------------------------------------------------------------------
# 2. Funciones de mejora de imagen
# -----------------------------------------------------------------------------------
def mejorar_contraste(imagen_gris):
    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
    return clahe.apply(imagen_gris)

def reducir_ruido(imagen_gris):
    return cv2.bilateralFilter(imagen_gris, d=5, sigmaColor=100, sigmaSpace=5)

def binarizar_imagen(imagen_gris):
    _, otsu = cv2.threshold(imagen_gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    adaptive = cv2.adaptiveThreshold(imagen_gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return cv2.bitwise_or(otsu, adaptive)

def aumentar_resolucion(imagen):
    return cv2.resize(imagen, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

# -----------------------------------------------------------------------------------
# 3. Preprocesamiento de imagen mejorado
# -----------------------------------------------------------------------------------
def preprocesar_imagen_mejorado(imagen_bgr):
    try:
        imagen_gris = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2GRAY)
        imagen_contraste = mejorar_contraste(imagen_gris)
        imagen_suavizada = reducir_ruido(imagen_contraste)
        imagen_binaria = binarizar_imagen(imagen_suavizada)
        imagen_enderezada = deskew(imagen_binaria)

        return imagen_enderezada
    except Exception as e:
        logging.error(f"Error en preprocesar_imagen_mejorado: {e}")
        return imagen_bgr  # Devuelve la imagen original si hay un error

# -----------------------------------------------------------------------------------
# 4. Función para realizar OCR combinando EasyOCR y Tesseract
# -----------------------------------------------------------------------------------
def realizar_ocr(imagen):
    try:
        texto_tesseract = pytesseract.image_to_string(imagen, config=CUSTOM_CONFIG, lang="spa+eng").strip()
        return texto_tesseract
    except Exception as e:
        logging.error(f"Error en realizar_ocr: {e}")
        return ""

def extraer_texto_imagen(imagen_pil):
    try:
        imagen_np = np.array(imagen_pil)
        imagen_preprocesada = preprocesar_imagen_mejorado(imagen_np)

        # Intentar con EasyOCR
        resultado_easyocr = reader.readtext(imagen_preprocesada, detail=0)
        texto_easyocr = ' '.join(resultado_easyocr).strip()

        # Intentar con Tesseract si EasyOCR no devuelve nada útil
        if not texto_easyocr or len(texto_easyocr) < 5:
            texto_tesseract = realizar_ocr(imagen_preprocesada)
            return f"{texto_easyocr}\n{texto_tesseract}".strip()

        return texto_easyocr
    except Exception as e:
        logging.error(f"Error en extraer_texto_imagen: {e}")
        return ""

# -----------------------------------------------------------------------------------
# 5. Función para extraer texto nativo de un PDF con pdfplumber
# -----------------------------------------------------------------------------------
def extraer_texto_pdf_plumber(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if pdf.pages:
                text = pdf.pages[0].extract_text()
                if text:
                    return text.strip()
    except Exception as e:
        logging.error(f"Error en extraer_texto_pdf_plumber: {e}")
    return ""

# -----------------------------------------------------------------------------------
# 6. Convertir PDF a imagen (primera página)
# -----------------------------------------------------------------------------------
def pdf_a_imagenes(pdf_path):
    try:
        return convert_from_path(pdf_path, dpi=600, first_page=1, last_page=1)
    except Exception as e:
        logging.error(f"Error en pdf_a_imagenes: {e}")
        return []

# -----------------------------------------------------------------------------------
# 7. Función para extraer texto de PDF (combinando pdfplumber y OCR)
# -----------------------------------------------------------------------------------
def extraer_texto_pdf(pdf_path):
    # 1. Intentar extraer con pdfplumber
    texto_plumber = extraer_texto_pdf_plumber(pdf_path)
    if texto_plumber:
        return texto_plumber

    # 2. Si no hay texto nativo, usar OCR
    paginas = pdf_a_imagenes(pdf_path)
    if paginas:
        return extraer_texto_imagen(paginas[0])

    return "No se pudo extraer texto del PDF"