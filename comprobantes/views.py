from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import render
from .models import Comprobante, DetalleComprobante
from .serializers import ComprobanteSerializer, DetalleComprobanteSerializer
from .ocr.easyocr import extraer_texto_imagen, extraer_texto_pdf
from .ocr.factura_processor import extract_tipo_comprobante, extract_numero_comprobante, extract_fecha_emision, extract_cuit_emisor, extract_nombre_emisor, extract_cuit_receptor, extract_nombre_receptor, extract_condicion_iva, extract_condicion_venta, extract_total, extract_moneda, extract_cae, extract_fecha_vencimiento_cae
import tempfile
import os
from django.http import JsonResponse
from rest_framework import status
from PIL import Image

class CrearComprobanteView(generics.CreateAPIView):
    queryset = Comprobante.objects.all()
    serializer_class = ComprobanteSerializer

class ListarComprobantesView(generics.ListAPIView):
    queryset = Comprobante.objects.all()
    serializer_class = ComprobanteSerializer

class ListarDetallesView(generics.ListAPIView):
    queryset = DetalleComprobante.objects.all()
    serializer_class = DetalleComprobanteSerializer

def cargar_archivo(request):
    return render(request, 'formulario_factura.html')

@api_view(['POST'])
def extraer_texto_factura(request):
    """
    API para extraer texto de un PDF o imagen de una factura.
    - Primero intenta extraer texto embebido en PDFs con pdfplumber.
    - Si no encuentra nada, usa OCR con EasyOCR y Tesseract como respaldo.
    """
    if 'archivo' not in request.FILES:
        return Response({'error': 'No se encontró el archivo'}, status=status.HTTP_400_BAD_REQUEST)

    archivo = request.FILES['archivo']
    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.' + archivo.name.split('.')[-1]) as temp_file:
            temp_file.write(archivo.read())
            temp_file_path = temp_file.name

        # Procesar archivo PDF
        if archivo.name.lower().endswith('.pdf'):
            texto_extraido = extraer_texto_pdf(temp_file_path)
        # Procesar imágenes (JPG, PNG, etc.)
        elif archivo.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            imagen = Image.open(temp_file_path)
            texto_extraido = extraer_texto_imagen(imagen)
        else:
            return Response({'error': 'Formato de archivo no soportado'}, status=status.HTTP_400_BAD_REQUEST)

        # Validar que el texto extraído sea legible
        if not texto_extraido.strip() or len(texto_extraido) < 5:
            return Response({'error': 'No se encontró texto legible en el archivo'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'texto': texto_extraido}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Error al procesar el archivo: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# =============================
# API: Extraer datos específicos de la factura
# =============================

@api_view(['POST'])
def extraer_datos_factura(request):
    """
    Extrae y devuelve un JSON con los campos:
      - tipo_comprobante
      - numero_comprobante
      - fecha_emision
      - cuit_emisor
      - nombre_emisor
      - cuit_receptor
      - nombre_receptor
      - condicion_iva
      - condicion_venta
      - total
      - moneda
      - cae
      - fecha_vencimiento_cae

    Si el archivo es PDF, intenta extraer el texto con pdfplumber; de lo contrario, utiliza OCR con EasyOCR.
    """
    if 'archivo' not in request.FILES:
        return Response({'error': 'No se encontró el archivo'}, status=status.HTTP_400_BAD_REQUEST)
    
    archivo = request.FILES['archivo']
    temp_file_path = None
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.' + archivo.name.split('.')[-1]) as temp_file:
            temp_file.write(archivo.read())
            temp_file_path = temp_file.name
        
        if archivo.name.lower().endswith('.pdf'):
            texto_extraido = extraer_texto_pdf(temp_file_path)
        elif archivo.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            imagen = Image.open(temp_file_path)
            texto_extraido = extraer_texto_imagen(imagen)
        else:
            return Response({'error': 'Formato de archivo no soportado'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not texto_extraido.strip():
            return Response({'error': 'No se encontró texto en el archivo'}, status=status.HTTP_404_NOT_FOUND)
        
        # Extraer cada campo usando las funciones definidas
        datos_factura = {
            "tipo_comprobante": extract_tipo_comprobante(texto_extraido),
            "numero_comprobante": extract_numero_comprobante(texto_extraido),
            "fecha_emision": extract_fecha_emision(texto_extraido),
            "cuit_emisor": extract_cuit_emisor(texto_extraido),
            "nombre_emisor": extract_nombre_emisor(texto_extraido),
            "cuit_receptor": extract_cuit_receptor(texto_extraido),
            "nombre_receptor": extract_nombre_receptor(texto_extraido),
            "condicion_iva": extract_condicion_iva(texto_extraido),
            "condicion_venta": extract_condicion_venta(texto_extraido),
            "total": extract_total(texto_extraido),
            "moneda": extract_moneda(texto_extraido),
            "cae": extract_cae(texto_extraido),
            "fecha_vencimiento_cae": extract_fecha_vencimiento_cae(texto_extraido)
        }
        
        # Retornar todos los campos, incluidos aquellos que queden como "Desconocido"
        return Response({'datos_factura': datos_factura}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': f'Error al procesar el archivo: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)