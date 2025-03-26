from django.urls import path
from .views import  extraer_datos_factura, extraer_texto_factura, CrearComprobanteView, ListarComprobantesView, ListarDetallesView
from . import views
urlpatterns = [
    path('crear/', CrearComprobanteView.as_view(), name='crear_comprobante'),
    path('comprobantes/', ListarComprobantesView.as_view(), name='listar_comprobantes'),
    path('detalles/', ListarDetallesView.as_view(), name='listar_detalles'),
    path('cargar-archivo/', views.cargar_archivo, name='cargar_archivo'),
    path('extraer-texto/', views.extraer_texto_factura, name='extraer_texto'),
    path('extraer-datos/', views.extraer_datos_factura, name='extraer_datos'),
]