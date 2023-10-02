from . import models
from rest_framework import serializers

class FelmeresQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FelmeresQuestions
        fields = "__all__"

class FelmeresekNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FelmeresNotes
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

class FelmeresekSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Felmeresek
        fields = "__all__"

class FelmeresItemsSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="coalesced_name") if  serializers.CharField(source="coalesced_name", null=True, blank=True) else serializers.CharField(source="name", null=True, blank=True)
    sku = serializers.CharField(read_only=True)

    class Meta:
        model = models.FelmeresItems
        fields = "__all__"
        read_only_fields = ['sku'] 


class OffersSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Offers
        fields = "__all__"

class QuestionProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QuestionProducts
        fields = "__all__"

class FilterItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FilterItems
        fields = "__all__"