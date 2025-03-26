from rest_framework import serializers
from .models import Comprobante, DetalleComprobante

class DetalleComprobanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleComprobante
        fields = '__all__'

class ComprobanteSerializer(serializers.ModelSerializer):
    detalles = DetalleComprobanteSerializer(many=True)

    class Meta:
        model = Comprobante
        fields = '__all__'

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        comprobante = Comprobante.objects.create(**validated_data)
        for detalle_data in detalles_data:
            DetalleComprobante.objects.create(comprobante=comprobante, **detalle_data)
        return comprobante