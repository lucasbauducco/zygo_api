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
    equalized = cv2.equalizeHist(imagen_gris)
    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
    return clahe.apply(imagen_gris)

def reducir_ruido(imagen_gris):
    bilateral = cv2.bilateralFilter(imagen_gris, d=5, sigmaColor=100, sigmaSpace=5)
    gaussian = cv2.GaussianBlur(bilateral, (5, 5), 0)
    median = cv2.medianBlur(gaussian, 3)
    return cv2.bilateralFilter(median, d=5, sigmaColor=100, sigmaSpace=5)

def binarizar_imagen(imagen_gris):
    otsu = cv2.threshold(imagen_gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1] # Devolvemos solo la imagen binarizada
    adaptive_gaussian = cv2.adaptiveThreshold(otsu, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    adaptive_mean = cv2.adaptiveThreshold(adaptive_gaussian, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    return adaptive_mean

def aumentar_resolucion(imagen):
    return cv2.resize(imagen, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)

def engrosar_texto(imagen_binaria):
    kernel = np.ones((2, 2), np.uint8)
    return cv2.dilate(imagen_binaria, kernel, iterations=1)

# -----------------------------------------------------------------------------------
# 3. Preprocesamiento de imagen mejorado
# -----------------------------------------------------------------------------------
def preprocesar_imagen_mejorado(imagen_bgr):
    try:
        imagen_gris = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2GRAY)
        imagen_suavizada = reducir_ruido(imagen_gris)
        imagen_binaria = binarizar_imagen(imagen_suavizada)
        imagen_contraste_clahe = mejorar_contraste(imagen_binaria)
        """
            esto no funciona empeora la imagen cada vez que la pasa por algun filtro
            imagen_gris = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2GRAY)
            imagen_contraste_clahe = mejorar_contraste(imagen_gris) # Aquí mejorar_contraste devuelve CLAHE aplicado
            imagen_suavizada = reducir_ruido(imagen_bgr)
            imagen_binaria = binarizar_imagen(imagen_bgr)
            imagen_enderezada = deskew(imagen_binaria) # El deskew opera sobre imagen binaria

        """
        return imagen_gris
    except Exception as e:
        logging.error(f"Error en preprocesar_imagen_mejorado: {e}")
        return imagen_bgr  # Devuelve la imagen original si hay un error

# -----------------------------------------------------------------------------------
# 4. Función para realizar OCR combinando EasyOCR y Tesseract
# -----------------------------------------------------------------------------------
def realizar_ocr(imagen):
    try:
        texto_tesseract_default = pytesseract.image_to_string(imagen, lang="spa+eng").strip()
        texto_tesseract_custom = pytesseract.image_to_string(imagen, config=custom_config, lang="spa+eng").strip()
        # Devolvemos el que tenga más texto (una heurística simple)
        if len(texto_tesseract_custom) > len(texto_tesseract_default):
            return texto_tesseract_custom
        else:
            return texto_tesseract_default
    except Exception as e:
        logging.error(f"Error en realizar_ocr: {e}")
        return ""

def extraer_texto_imagen(imagen_pil):
    try:
        imagen_np = np.array(imagen_pil)
        imagen_preprocesada = preprocesar_imagen_mejorado(imagen_np)

        # Aumentar resolución ANTES del OCR puede ayudar con texto borroso
        imagen_alta_resolucion = aumentar_resolucion(imagen_preprocesada)
        # Intentar con EasyOCR con la imagen de alta resolución
        resultado_easyocr = reader.readtext(imagen_alta_resolucion, detail=0, paragraph=True) # Intentamos leer por párrafos
        texto_easyocr = ' '.join(resultado_easyocr).strip()

        # Intentar con Tesseract si EasyOCR no devuelve nada útil o es muy corto
        if not texto_easyocr or len(texto_easyocr) < 10: # Aumentamos el umbral de longitud
            texto_tesseract = realizar_ocr(imagen_alta_resolucion)
            return f"{texto_easyocr}\n[Tesseract] {texto_tesseract}".strip()

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
        # Aumentamos el DPI para obtener imágenes de mayor resolución
        return convert_from_path(pdf_path, dpi=400, first_page=1, last_page=1)
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