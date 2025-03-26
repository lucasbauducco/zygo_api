from django.shortcuts import render

def formulario_factura(request):
    return render(request, 'formulario_factura.html')