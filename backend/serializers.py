from . import models
from rest_framework import serializers

class FelemeresekSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Felmeresek
        fields = "__all__"

class FelmeresekNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FelmeresekNotes
        fields = "__all__"

class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Products
        fields = "__all__"

class ProductAttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductAttributes
        fields = "__all__"