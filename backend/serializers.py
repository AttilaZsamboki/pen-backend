from . import models
from rest_framework import serializers

class FelemeresekSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Felmeresek
        fields = "__all__"