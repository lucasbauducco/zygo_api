# ocr/facturita.py
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from rest_framework import status
import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

# Función para extraer texto desde una imagen o PDF
def extraer_texto(archivo):
    try:
        # Si el archivo es un PDF, convertimos cada página en una imagen
        if archivo.name.endswith('.pdf'):
            images = convert_from_path(archivo, first_page=1, last_page=1)  # Convierte la primera página del PDF
            image = images[0]  # Tomamos la primera imagen generada
        else:
            image = Image.open(archivo)  # Si es una imagen, la abrimos directamente

        texto = pytesseract.image_to_string(image, lang='spa')
        return texto
    except Exception as e:
        return None, f"Error al procesar el archivo: {str(e)}"

# Función para procesar la factura
def procesar_factura(archivo):
    texto_extraido, error = extraer_texto(archivo)
    
    if not texto_extraido:
        return {"error": error or "No se pudo extraer texto de la imagen"}
    
    # Procesar texto extraído usando expresiones regulares para capturar los datos
    comprobante_data = {
        "tipo_comprobante": "Desconocido",
        "numero_comprobante": "Desconocido",
        "fecha_emision": "Desconocido",
        "cuit_emisor": "Desconocido",
        "nombre_emisor": "Desconocido",
        "cuit_receptor": "Desconocido",
        "nombre_receptor": "Desconocido",
        "condicion_iva": "Desconocido",
        "condicion_venta": "Desconocido",
        "total": "Desconocido",
        "moneda": "ARS",  # Moneda por defecto
        "cae": "Desconocido",
        "fecha_vencimiento_cae": "Desconocido"
    }

    
    # Extraer tipo de comprobante
    tipo_comprobante = re.search(r"(Facturas|Codigo\s*006|Codigo\s*5|Cod\s*201)", texto_extraido)
    comprobante_data["tipo_comprobante"] = tipo_comprobante.group(0) if tipo_comprobante else "Desconocido"
    
    # Extraer número de comprobante
    numero_comprobante = re.search(r"(Nro\.?\s*Comp\.?:?\s*(\d{4}-\d{8}|\d{4}-\d{7}|\d{4}-\d{6}))|(P\.V\.?\s*N°\s*(\d+)\s*T\.\s*(\d+))", texto_extraido)
    comprobante_data["numero_comprobante"] = numero_comprobante.group(2) if numero_comprobante else "Desconocido"
    
    # Extraer fecha de emisión
    fecha_emision = re.search(r"Fecha de (Emisión|Vencimiento):?\s*(\d{2}/\d{2}/\d{4}|\d{2}/\d{2}/\d{2})", texto_extraido)
    comprobante_data["fecha_emision"] = fecha_emision.group(2) if fecha_emision else "Desconocido"
    
    # Extraer CUIT emisor
    cuit_emisor = re.search(r"(C\.U\.I\.T\.?\s*[:\s]*\d{2}-\d{8}-\d{1}|\d{11})", texto_extraido)
    comprobante_data["cuit_emisor"] = cuit_emisor.group(0) if cuit_emisor else "Desconocido"
    
    # Extraer nombre del emisor
    nombre_emisor = re.search(r"(Razón Social:?\s*([A-Za-z0-9\s\S]+))", texto_extraido)
    comprobante_data["nombre_emisor"] = nombre_emisor.group(2) if nombre_emisor else "Desconocido"
    
    # Extraer CUIT receptor
    cuit_receptor = re.search(r"(CUIT:?\s*\d{2}-\d{8}-\d{1}|\d{11})", texto_extraido)
    comprobante_data["cuit_receptor"] = cuit_receptor.group(0) if cuit_receptor else "Desconocido"
    
    # Extraer nombre del receptor
    nombre_receptor = re.search(r"(Apellido y Nombre|Razón Social:?\s*([A-Za-z0-9\s\S]+))", texto_extraido)
    comprobante_data["nombre_receptor"] = nombre_receptor.group(2) if nombre_receptor else "Desconocido"
    
    # Extraer condición de IVA
    condicion_iva = re.search(r"(Responsable Inscripto|Responsable Monotributo|IVA\s*[\d\.]+)", texto_extraido)
    comprobante_data["condicion_iva"] = condicion_iva.group(0) if condicion_iva else "Desconocido"
    
    # Extraer condición de venta
    condicion_venta = re.search(r"(Contado|Crédito|Financiación|Débito Automático)", texto_extraido)
    comprobante_data["condicion_venta"] = condicion_venta.group(0) if condicion_venta else "Desconocido"
    
    # Extraer total
    total = re.search(r"(TOTAL|Importe Total:?\s*([\d\.,]+))", texto_extraido)
    comprobante_data["total"] = total.group(2) if total else "Desconocido"
    
    # Extraer moneda
    moneda = re.search(r"(Importe Total:\s*(\w+))", texto_extraido)
    comprobante_data["moneda"] = moneda.group(2) if moneda else "ARS"
    
    # Extraer CAE
    cae = re.search(r"(CAE N°:?\s*\d+)", texto_extraido)
    comprobante_data["cae"] = cae.group(0) if cae else "Desconocido"
    
    # Extraer fecha vencimiento CAE
    fecha_vencimiento = re.search(r"(Fecha de Vencimiento CAE:?\s*(\d{2}/\d{2}/\d{4}))", texto_extraido)
    comprobante_data["fecha_vencimiento_cae"] = fecha_vencimiento.group(2) if fecha_vencimiento else "Desconocido"
    
    # Detalles de los productos (por ejemplo)
    detalles_data = []
    productos = re.findall(r"([A-Za-z\s]+)\s*([0-9]+)\s*([0-9\.]+)", texto_extraido)  # Esto es un ejemplo
    for producto in productos:
        detalles_data.append({
            "producto": producto[0],
            "cantidad": producto[1],
            "precio": producto[2]
        })
    
    return {
        "comprobante_data": comprobante_data,
        "detalles_data": detalles_data
    }