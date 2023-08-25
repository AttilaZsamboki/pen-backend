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

class FiltersSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Filters
        fields = "__all__"

class QuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Questions
        fields = "__all__"

class ProductTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductTemplate
        fields = "__all__"

class TemplatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Templates
        fields = "__all__"