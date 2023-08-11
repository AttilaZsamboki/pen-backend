from . import models
from rest_framework import serializers

class TemplatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DatauploadTabletemplates
        fields = '__all__'