# Proyecto de Procesamiento de Facturas con OCR y Regex

Este proyecto tiene como objetivo extraer información relevante de imágenes de facturas utilizando técnicas de Reconocimiento Óptico de Caracteres (OCR) y expresiones regulares. (El proyecto tiene varios Errores a la hora de procesar las imagenes y captar optimamente la info.)

## Tabla de Contenidos

- [Instalación](#instalación)
- [Dependencias](#dependencias)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Documentación del Código](#documentación-del-código)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)

## Instalación

Sigue estos pasos para instalar y configurar el proyecto en tu entorno local:

1.  **Clonar el repositorio:**
    ```bash
    git clone [URL_DEL_REPOSITORIO]
    cd [NOMBRE_DEL_REPOSITORIO]
    ```
    Reemplaza `[URL_DEL_REPOSITORIO]` con la URL de tu repositorio de Git y `[NOMBRE_DEL_REPOSITORIO]` con el nombre de la carpeta del proyecto.

2.  **Crear un entorno virtual (recomendado):**
    ```bash
    python -m venv env
    source env/bin/activate  # En Linux/macOS
    env\Scripts\activate  # En Windows
    ```

3.  **Instalar las dependencias:**
    El proyecto utiliza las siguientes librerías de Python, que se pueden instalar usando `pip`:
    ```bash
    pip install -r requirements.txt
    ```
    Asegúrate de tener Tesseract instalado en tu sistema operativo si planeas usarlo. Las instrucciones de instalación varían según el sistema operativo. Consulta la documentación de Tesseract para más detalles.

## Dependencias

Este proyecto depende de las siguientes librerías de Python:

* [EasyOCR](https://www.jaided.ai/easyocr/): Para realizar el Reconocimiento Óptico de Caracteres (OCR).
* [OpenCV (cv2)](https://opencv.org/): Para el preprocesamiento de imágenes (mejora de contraste, reducción de ruido, binarización, etc.).
* [NumPy](https://numpy.org/): Para la manipulación eficiente de arrays de imágenes.
* [Pillow (PIL)](https://pillow.readthedocs.io/en/stable/): Para trabajar con archivos de imagen.
* [pytesseract](https://pypi.org/project/pytesseract/): (Opcional) Si se utiliza Tesseract directamente como motor de OCR.
* [Torch](https://pytorch.org/): (Dependencia de EasyOCR) Framework de aprendizaje automático.

Asegúrate de tener estas dependencias instaladas como se describe en la sección de [Instalación](#instalación).

## Uso

Para utilizar la funcionalidad de procesamiento de facturas, necesitas interactuar con el formulario de carga de archivos disponible en la siguiente URL:
http://127.0.0.1:8000/api/cargar_archivo/
Ejemplo:

Puedes acceder a este formulario a través de un navegador web o mediante una petición HTTP POST desde cualquier cliente (por ejemplo, `curl`, `Postman`, una aplicación web personalizada, etc.).

**A través de un formulario web (navegador):**

1.  Abre la URL `http://127.0.0.1:8000/api/cargar_archivo/` en tu navegador web.
2.  Deberías ver un formulario que te permite seleccionar un archivo.
3.  Haz clic en el botón "Seleccionar archivo" y elige la imagen de la factura (en formato JPG, PNG, etc.) o el archivo PDF que deseas procesar.
4.  Haz clic en el botón "Subir y Procesar" (o el texto que hayas definido en tu formulario).
5.  El servidor procesará el archivo, realizará el OCR y la extracción de información, y la respuesta se mostrará en tu navegador (generalmente como un JSON).

**A través de una petición HTTP POST (ejemplo con `curl`):**

Puedes enviar una petición `POST` con el archivo adjunto utilizando herramientas de línea de comandos como `curl`.

```bash
curl -X POST -F "archivo=@/ruta/a/tu/factura.jpg" [http://127.0.0.1:8000/api/cargar_archivo/](http://127.0.0.1:8000/api/cargar_archivo/)

2.  **Interpretar la salida:**
    El script procesará la imagen, extraerá el texto mediante OCR y luego intentará identificar la información relevante utilizando expresiones regulares. La salida se mostrará en la consola (o se guardará en un archivo, según tu implementación).

    Ejemplo de salida:
    ```json
    {
        "comprobante_data": {
            "tipo_comprobante": "Factura A",
            "numero_comprobante": "0001-00000001",
            "fecha_emision": "2024/07/15",
            "cuit_emisor": "30123456789",
            "nombre_emisor": "EMPRESA EJEMPLO S.A.",
            "cuit_receptor": "20987654321",
            "nombre_receptor": "CLIENTE FINAL",
            "total": "1234.56",
            "moneda": "ARS",
            "cae": "12345678901234",
            "fecha_vencimiento_cae": "2024/07/25"
        },
        "detalles_data": [
            {
                "producto": "Artículo 1",
                "cantidad": "2",
                "precio": "100.00"
            },
            {
                "producto": "Artículo 2",
                "cantidad": "1",
                "precio": "1034.56"
            }
        ]
    }
    ```

## Estructura del Proyecto

Describe la organización de los archivos y carpetas dentro del proyecto.

Ejemplo:
[ZYGO_API]/
├── ocr/easyocr.py            # Script para la configuración y ejecución de EasyOCR
├── ocr/factura_processor.py  # Script con las funciones para procesar el texto extraído , usar regex y Script con funciones de preprocesamiento de imágenes 
├── requirements.txt      # Lista de dependencias del proyecto
└── ... 
## Documentación del Código

* **`easyocr.py`:**
    * `reader = easyocr.Reader(['es', 'en'])`: Inicialización del lector de EasyOCR para los idiomas español e inglés.
    * `preprocesar_imagen_mejorado(imagen_np)`: Función que aplica una serie de pasos de preprocesamiento a la imagen (escala de grises, mejora de contraste, reducción de ruido, binarización, corrección de inclinación).
    * `aumentar_resolucion(imagen)`: Función para aumentar la resolución de la imagen.
    * `realizar_ocr(imagen_np)`: (Si usas Tesseract) Función para realizar OCR con Tesseract.

* **`factura_processor.py`:**
    * `extract_tipo_comprobante(texto)`: Función para extraer el tipo de comprobante usando expresiones regulares.
    * `extract_numero_comprobante(texto)`: Función para extraer el número de comprobante usando expresiones regulares.
    * `extract_fecha_emision(texto)`: Función para extraer la fecha de emisión usando expresiones regulares.
    * ... (Describe otras funciones de extracción)
    * `procesar_factura(texto_extraido, error=None)`: Función principal que toma el texto extraído por OCR y aplica las funciones de extracción para obtener la información de la factura.

## Contribuciones

Ejemplo:

Las contribuciones son bienvenidas. Si encuentras algún error o tienes alguna sugerencia de mejora, por favor:

1.  Informa el problema creando un nuevo "Issue" en este repositorio.
2.  Si deseas contribuir con código, haz un fork del repositorio, crea una rama con tus cambios y envía un "Pull Request".

## Licencia
