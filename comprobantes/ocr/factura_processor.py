import re

# =============================
# Funciones de extracción individual
# =============================

def extract_tipo_comprobante(texto):
    """
    Extrae el tipo de comprobante.
    Puede aparecer como:
      - "Facturas 001"
      - "Codigo 006"
      - "Cod 201"
      - "COD. 06"
      - "Cód. 082"
      - "FACTURA A"
      - "FACTURA B"
      - "FACTURA C"
      - "FACTURA E"

    Retorna solo el número del comprobante o el tipo de factura (A, B, C, etc.).
    """
    # Intentar capturar "Facturas 001", "Codigo 006", etc.
    match = re.search(r"(?:Facturas|Codigo|Cod\.?|COD\.?|Cód\.)\s*(\d+)", texto, re.IGNORECASE)
    if match:
        return match.group(1)

    # Intentar capturar "FACTURA A", "FACTURA B", etc.
    match = re.search(r"FACTURA\s+([A-Z])", texto, re.IGNORECASE)
    if match:
        return f"Factura {match.group(1)}"

    return "Desconocido"

def extract_numero_comprobante(texto):
    """Extrae el número de comprobante en distintos formatos."""
    match = re.search(
        r"(?:Nro[._]?\s*(\d{4,5})\s*-?\s*(\d{6,8}))"  # Formato: "Nro. 02646 - 00115536" o "Nro_ 02646 00115836"
        r"|(?:Nro\.?\s*(?:Comp\.?:\s*)?(\d{4}-\d{6,8}))"  # Formato: "Nro. Comp.: 02646-00115536"
        r"|(?:P\.V\.?\s*N°\s*(\d+)\s*T\.\s*(\d+))",  # Formato: "P.V. N° 02646 T. 00115536"
        texto, re.IGNORECASE
    )

    if match:
        if match.group(1) and match.group(2):
            return f"{match.group(1)}-{match.group(2)}"  # Unir con guion si se capturaron por separado
        elif match.group(3):  
            return match.group(3)  # Formato "Nro. Comp.: 02646-00115536"
        elif match.group(4) and match.group(5):
            return f"{match.group(4)} T. {match.group(5)}"  # Formato "P.V. N° 02646 T. 00115536"

    return "Desconocido"

def extract_fecha_emision(texto):
    """
    Extrae la fecha de emisión, ya sea que aparezca como:
      - "Fecha: 15/07/2024"
      - "Fecha de Emisión: 15/07/2024"
      - "Fecha de Vencimiento: 15/07/2024"
      - "Fecha: 22/03/25"
    """
    match = re.search(
        r"(?:Fecha(?: de (?:Emisión|Vencimiento))?:?\s*)(\d{2}/\d{2}/\d{4}|\d{2}/\d{2}/\d{2})",
        texto,
        re.IGNORECASE
    )
    return match.group(1) if match else "Desconocido"


def extract_cuit_emisor(texto):
    """Extrae el CUIT del emisor."""
    match = re.search(
        r"(?:C\.U\.I\.T\.?|CUIT|CUIT Nro\.?)\s*[:\s]*([\d\-]{13}|\d{11})", 
        texto, re.IGNORECASE
    )
    return match.group(1) if match else "Desconocido"

def extract_nombre_emisor(texto):
    """
    Extrae el nombre del emisor.
    Primero intenta capturar el valor que sigue al patrón "Razón Social:".
    Si no se encuentra, busca una cadena que contenga indicadores de sociedades
    comunes (por ejemplo, S.A., S.L., S.R.L., S.C.P., S.A.C., E.I.R.L., S.p.A., S.r.l., S.a.s, S.n.c., Coop., S.L.L.).
    Retorna el nombre encontrado o "Desconocido" si no se halla coincidencia.
    """
    # Intentar extraer usando "Razón Social:"
    match = re.search(r"Raz[oó]n Social:?\s*([A-Za-z0-9\s\.,\-&]+)", texto, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Definir una expresión regular que agrupe las abreviaturas de sociedades
    sociedades = r"(?:S\.A\.|S\.L\.|S\.R\.L\.|S\.C\.P\.|S\.A\.C\.|E\.I\.R\.L\.|S\.p\.A\.|S\.r\.l\.|S\.a\.s\.?|S\.n\.c\.|Coop\.|S\.L\.L\.)"
    # Buscar una cadena que contenga alguna de estas abreviaturas
    match = re.search(r"([A-Za-z0-9\s\.,\-&]+"+sociedades+r")", texto, re.IGNORECASE)
    if match:
        return match.group(0).strip()
    
    return "Desconocido"

def extract_cuit_receptor(texto):
    """Extrae el CUIT del receptor."""
    match = re.search(
        r"(CUIT:?\s*\d{2}-\d{8}-\d{1}|\d{11})", 
        texto, re.IGNORECASE
    )
    return match.group(0) if match else "Desconocido"

def extract_nombre_receptor(texto):
    """
    Extrae el nombre del receptor desde diferentes formatos, incluyendo:
      - "Cliente: BAUDUCCO LUCAS (40266139)"
      - "Apellido y Nombre: BAUDUCCO LUCAS"
      - "Razón Social: EMPRESA XYZ S.A."
    
    Retorna el nombre encontrado o "Desconocido" si no hay coincidencias.
    """
    # Intentar extraer desde "Cliente: NOMBRE (DNI/CUIT)"
    match = re.search(r"Cliente:\s*([A-Za-z\s]+)\s*\(\d+\)", texto, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Intentar extraer desde "Apellido y Nombre: NOMBRE"
    match = re.search(r"Apellido y Nombre:?\s*([A-Za-z\s]+)", texto, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Intentar extraer desde "Razón Social: EMPRESA XYZ S.A."
    match = re.search(r"Raz[oó]n Social:?\s*([A-Za-z0-9\s\.,\-&]+)", texto, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    return "Desconocido"

def extract_condicion_iva(texto):
    """Extrae la condición de IVA."""
    match = re.search(
        r"(Responsable Inscripto|Responsable Monotributo|IVA\s*[\d\.]+)", 
        texto, re.IGNORECASE
    )
    return match.group(0) if match else "Desconocido"

def extract_condicion_venta(texto):
    """Extrae la condición de venta."""
    match = re.search(
        r"(Contado|Crédito|Financiación|Débito Automático)", 
        texto, re.IGNORECASE
    )
    return match.group(0) if match else "Desconocido"

def extract_total(texto):
    """
    Extrae el importe total de la factura.
    Puede aparecer como:
      - "Importe Total: 4.000.000,22"
      - "TOTAL                     4.000.000,22"
      - "Total Factura: 1234,56"
      - "TOTAL: 1,234.56"
      - "TOTAL $ 9087 , 00"
      - "T@7A 9087,00"
    
    Se captura tanto el formato con puntos y comas (4.000.000,22) como el formato con comas y puntos (1,234.56),
    y también el formato con el símbolo de peso o caracteres extra.
    
    Retorna el importe encontrado o "Desconocido" si no se halla coincidencia.
    """
    match = re.search(
        r"(?:TOTAL|Importe Total|Total Factura|T@7A)[:\s]*[$]?\s?([\d\.,]+)", 
        texto, re.IGNORECASE
    )
    return match.group(1).strip() if match else "Desconocido"

def extract_moneda(texto):
    """Extrae la moneda (por defecto 'ARS')."""
    match = re.search(
        r"(Importe Total:\s*(\w+))", 
        texto, re.IGNORECASE
    )
    return match.group(2) if match and match.group(2) else "ARS"

def extract_cae(texto):
    """
    Extrae el CAE (Código de Autorización Electrónico).
    Puede aparecer como:
      - "CAE N°: 74297978398739"
      - "C.A.E : 74297978398739"
      - "C.A.E.: 74297978398739"
    
    Retorna el número del CAE o "Desconocido" si no se encuentra.
    """
    match = re.search(
        r"(?:C\.?A\.?E\.?\s*:?|CAE N°:?\s*)(\d{14})", 
        texto, re.IGNORECASE
    )
    return match.group(1).strip() if match else "Desconocido"

def extract_fecha_vencimiento_cae(texto):
    """
    Extrae la fecha de vencimiento del CAE.
    Puede aparecer como:
      - "Fecha de Vencimiento CAE: 25/07/2024"
      - "Fec. Venc.: 25/07/2024"

    Retorna la fecha en formato DD/MM/YYYY o "Desconocido" si no se encuentra.
    """
    match = re.search(
        r"(?:Fecha de Vencimiento CAE|Fec\.? Venc\.)\s*:? (\d{2}/\d{2}/\d{4})", 
        texto, re.IGNORECASE
    )
    return match.group(1).strip() if match else "Desconocido"

def extract_detalles(texto):
    """
    Extrae detalles de productos.
    Se busca un patrón de: nombre_producto, cantidad y precio.
    Este regex es un ejemplo y puede necesitar ajustes según el formato.
    """
    detalles = []
    productos = re.findall(r"([A-Za-z\s]+)\s*([0-9]+)\s*([0-9\.,]+)", texto)
    for producto in productos:
        detalles.append({
            "producto": producto[0].strip(),
            "cantidad": producto[1],
            "precio": producto[2]
        })
    return detalles

# =============================
# Función principal para procesar la factura
# =============================

def procesar_factura(texto_extraido, error=None):
    """
    Procesa el texto extraído de una factura y retorna un diccionario con:
      - comprobante_data: Datos generales de la factura.
      - detalles_data: Lista de productos o detalles encontrados.
    En caso de error o texto vacío, retorna un diccionario de error.
    """
    if not texto_extraido or not texto_extraido.strip():
        return {"error": error or "No se pudo extraer texto de la imagen"}

    comprobante_data = {
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

    detalles_data = extract_detalles(texto_extraido)

    return {
        "comprobante_data": comprobante_data,
        "detalles_data": detalles_data
    }

# =============================
# Ejemplo de uso
# =============================
if __name__ == "__main__":
    # Supongamos que 'texto_extraido' es el resultado obtenido por OCR o extracción nativa del PDF.
    texto_extraido = """
    Facturas
    Nro. Comp.: 4001-00054017
    Fecha de Emisión: 15/07/2024
    C.U.I.T.: 30-53284754-7
    Razón Social: Bazar Avenida S.A.
    CUIT: 30-53284754-7
    Apellido y Nombre: BAUDUCCO LUCAS
    Responsable Inscripto
    Condición de Venta: Contado
    TOTAL Importe Total: 449.999,00
    CAE N°: 74297978398739
    Fecha de Vencimiento CAE: 25/07/2024
    ProductoX 1 449.999,00
    """
    resultado = procesar_factura(texto_extraido)
    print("Resultado de procesamiento de la factura:")
    print(resultado)