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
    match = re.search(r"(?:Factura|Ticket|T[i1]cket)\s*[A-Z]?", texto, re.IGNORECASE)
    if match:
        return match.group(0).strip()
    return "Desconocido"

def extract_numero_comprobante(texto):
    """Extrae el número de comprobante en distintos formatos."""
    match = re.search(r"(?:Nro\.?|N[o°]\.?)\s*[T\.?]\s*(\d+)", texto, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"(?:Mo\.?T\.?)\s*(\d+)", texto, re.IGNORECASE) # Captura "Mo.T.00135246"
    if match:
        return match.group(1)
    match = re.search(
        r"(?:Nro[._]?\s*(\d{3,5})\s*[-_\s]?\s*(\d{6,8}))"
        r"|(?:Nro\.?\s*(?:Comp\.?[:\s]*)?(\d{3,5}[-_\s]\d{6,8}))"
        r"|(?:P\.?V\.?\s*N[o°]\s*(\d+)\s*T\.?\s*(\d+))",
        texto, re.IGNORECASE
    )
    if match:
        if match.group(1) and match.group(2):
            return f"{match.group(1)}-{match.group(2)}"
        elif match.group(3):
            return match.group(3).replace('-', '-').replace('_', '-').replace(' ', '-')
        elif match.group(4) and match.group(5):
            return f"{match.group(4)} T. {match.group(5)}"
    return "Desconocido"

def extract_fecha_emision(texto):
    """
    Extrae la fecha de emisión, ya sea que aparezca como:
      - "Fecha: 15/07/2024"
      - "Fecha de Emisión: 15/07/2024"
      - "Fecha de Vencimiento: 15/07/2024"
      - "Fecha: 22/03/25"
    """
    match = re.search(r"(?:F[Ee][Cc]ha)\s*(\d{2}[-/\s]\d{2}[-/\s]\d{2,4})", texto, re.IGNORECASE)
    if match:
        fecha = match.group(1).replace('-', '/').replace(' ', '/')
        if len(fecha.split('/')[2]) == 2:
            año_corto = fecha.split('/')[2]
            año_completo = f"20{año_corto}" if int(año_corto) <= 25 else f"19{año_corto}"
            return f"{fecha.split('/')[0]}/{fecha.split('/')[1]}/{año_completo}"
        return fecha
    return "Desconocido"

def extract_hora_emision(texto):
    match = re.search(r"(?:Hora)\s*(\d{2}[:;]\d{2}[:;]\d{2})", texto, re.IGNORECASE)
    if match:
        return match.group(1).replace(';', ':')
    return "Desconocido"

def extract_cuit_emisor(texto):
    """Extrae el CUIT del emisor."""
    match = re.search(r"(?:C[uU][iI][tT])[:\s]*Nros?[:\s]*([\d]{11,13})", texto, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"([\d]{2}-[\d]{8}-[\d]{1})", texto) # Otro formato común
    if match:
        return match.group(0)
    return "Desconocido"

def extract_nombre_emisor(texto):
    """
    Extrae el nombre del emisor.
    Primero intenta capturar el valor que sigue al patrón "Razón Social:".
    Si no se encuentra, busca una cadena que contenga indicadores de sociedades
    comunes (por ejemplo, S.A., S.L., S.R.L., S.C.P., S.A.C., E.I.R.L., S.p.A., S.r.l., S.a.s, S.n.c., Coop., S.L.L.).
    Retorna el nombre encontrado o "Desconocido" si no se halla coincidencia.
    """
    # Intentar extraer usando "Razón Social:"
    lineas = texto.splitlines()
    for linea in lineas:
        linea = linea.strip()
        if linea.isupper() and len(linea.split()) > 1:
            return linea
        elif re.search(r"^[A-Z][a-z]+", linea): # Empieza con mayúscula
            return linea
    return "Desconocido"

def extract_cuit_receptor(texto):
    """Extrae el CUIT del receptor."""
    match = re.search(
        r"(CUIT[:\s]*[\d\-_]{2}-[\d\-_]{8}-[\d\-_]{1}|\d{11})",
        texto, re.IGNORECASE
    )
    if match:
        return match.group(0).replace('-', '')
    return "Desconocido"

def extract_nombre_receptor(texto):
    """
    Extrae el nombre del receptor desde diferentes formatos, incluyendo:
      - "Cliente: BAUDUCCO LUCAS (40266139)"
      - "Apellido y Nombre: BAUDUCCO LUCAS"
      - "Razón Social: EMPRESA XYZ S.A."
    
    Retorna el nombre encontrado o "Desconocido" si no hay coincidencias.
    """
    match = re.search(r"Cliente[:\s]*([A-Za-z\s]+)\s*\(?\d+[^\)]*\)?", texto, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"(?:Apellido\s*y\s*Nombre|Nombre)\s*[:\s]*([A-Za-z\s]+)", texto, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Buscar líneas que contengan "A CONSUMIDOR FINAL" o similar
    match = re.search(r"(A\s+CONSUMIDOR\s+FINAL)", texto, re.IGNORECASE)
    if match:
        return match.group(1)
    return "Desconocido"

def extract_condicion_iva(texto):
    """Extrae la condición de IVA."""
    match = re.search(r"(?:IvA|IVA)\s*(?:Respoksable|Responsable)\s*(?:InscripTo|Inscripto)", texto, re.IGNORECASE)
    if match:
        return "Responsable Inscripto"
    return "Desconocido"

def extract_condicion_venta(texto):
    """Extrae la condición de venta."""
    match = re.search(
        r"(Contado|Cr[eé]dito|Financiaci[oó]n|D[eé]bito\s*Autom[aá]tico)",
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
    match = re.search(r"(?:Total)\s*([\d\.,]+)", texto, re.IGNORECASE)
    if match:
        return match.group(1).replace('.', '').replace(',', '.')
    return "Desconocido"

def extract_moneda(texto):
    """Extrae la moneda (por defecto 'ARS')."""
    match = re.search(r"(?:TOTAL\s*(\w+))", texto, re.IGNORECASE) # Buscar moneda cerca de "TOTAL"
    return match.group(1) if match else "ARS"

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
        r"(?:C\.?\s*A\.?\s*E\.?[:\s]*|CAE\s*N[o°][:.\s]*)(\d{14})",
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
    match = re.search(r"(?:Fecha\s*de\s*Vencimiento\s*CAE|Fec\.?\s*Venc\.?)[:\s]*(\d{2}[-/\s]\d{2}[-/\s]\d{4})",
        texto, re.IGNORECASE
    )
    if match:
        return match.group(1).replace('-', '/').replace(' ', '/')
    return "Desconocido"

def extract_detalles(texto):
    """
    Extrae detalles de productos.
    Se busca un patrón de: nombre_producto, cantidad y precio.
    Este regex es un ejemplo y puede necesitar ajustes según el formato.
    """
    detalles = []
    lineas = texto.splitlines()
    for linea in lineas:
        match = re.search(r"(\d+[\.,]?\d*)\s*[xX]\s*([\d\.,]+)\s+([A-Za-z0-9\s\.\-,]+)", linea)
        if match:
            cantidad = match.group(1).replace('.', '').replace(',', '.')
            precio_unitario = match.group(2).replace('.', '').replace(',', '.')
            descripcion = match.group(3).strip()
            detalles.append({"cantidad": cantidad, "precio_unitario": precio_unitario, "descripcion": descripcion})
        else:
            match = re.search(r"([A-Za-z0-9\s\.\-,]+)\s+([\d\.,]+)", linea)
            if match:
                descripcion = match.group(1).strip()
                precio = match.group(2).replace('.', '').replace(',', '.')
                detalles.append({"cantidad": "1", "precio": precio, "descripcion": descripcion})
    return detalles
# =============================
# Función principal para procesar la factura
# =============================

def procesar_factura(texto_extraido, error=None):
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
    texto_extraido_ticket = """
    2 -CARREFOUR-
    VICENTE LOPEZ.
    Orientacion al Consumidor Pcia
    de Bs.As 0800-222-9042
    INC S.A.
    CUIT Nro.: 30-68731043-4
    Av Libertador 215 - Vte. Lope.
    Pcia. Bs.As(B1638PEB)
    IVA RESPONSABLE INSCRIPTO
    A CONSUMIDOR FINAL
    P.V. Nro.: 0153          Nro. T. 00220314
    Fecha 17/03/19           Hora 10:48:36
    MERMELADA DE ROSA MO
    SQUEIA EL BROCAL X 4          159.00
    7798088960363
    2.0000 x 120,0000
    PAN ARTESANAL BIMBO
    X 500 GRS                    240.00
    7796989008542
    2do60%-PAN BLAN-BIM          -72.00
    BONIF.                       29.37
    RECARGO VISA 2 CUOTAS CON
    TOTAL                       355,37
    VISA                        355.37
    Suma de sus pagos           355.37
    Su Vuelto                     0.00
    BONIF. PROMOCIONES           72.00
    Articulos 3
    Cajero 33-Carrizo Graciela
    0034 0002 017 033    17 03 19 10 50 AC-00
            V: 22.00 Hera
    2527  Registro Nro.: PE01003516
    """
    resultado_ticket = procesar_factura(texto_extraido_ticket)
    print("\nResultado del procesamiento del ticket:")
    print(resultado_ticket)