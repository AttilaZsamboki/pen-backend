from . import models
from rest_framework import serializers


class FelmeresQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FelmeresQuestions
        fields = "__all__"


class FelmeresNotesSerializer(serializers.ModelSerializer):
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


class FelmeresekSerializer(serializers.ModelSerializer):
    offer_status = serializers.CharField(
        required=False, allow_null=True, read_only=True
    )

    class Meta:
        model = models.Felmeresek
        fields = "__all__"
        read_only_fields = ["offer_status"]


class FelmeresItemsSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(required=False, read_only=True)
    create_name = serializers.CharField(
        required=False, allow_null=True, write_only=True
    )
    sku = serializers.CharField(read_only=True)

    class Meta:
        model = models.FelmeresItems
        fields = "__all__"
        read_only_fields = ["sku"]

    def get_name(self, obj):
        try:
            return obj.coalesced_name
        except AttributeError:
            return obj.name

    def create(self, validated_data):
        name = validated_data.pop("create_name", None)
        instance = super().create(validated_data)
        if name is not None:
            instance.name = name
            instance.save()
        return instance


class QuestionProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QuestionProducts
        fields = "__all__"


class FilterItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FilterItems
        fields = "__all__"


class FelmeresPicturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FelmeresPictures
        fields = "__all__"


class UserRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserRoles
        fields = "__all__"


class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Roles
        fields = "__all__"


class MiniCrmAdatlapokSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MiniCrmAdatlapok
        fields = [
            "Id",
            "Name",
            "CategoryId",
            "StatusId",
            "ContactId",
            "Cim2",
            "FelmeresiDij",
            "Telepules",
            "Iranyitoszam",
            "Orszag",
            "Felmero2",
            "IngatlanKepe",
            "CreatedAt",
            "FelmeresiDij",
        ]


class MunkadijSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Munkadij
        fields = "__all__"


class FelmeresMunkadijakSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FelmeresMunkadijak
        fields = "__all__"


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Settings
        fields = "__all__"


class AppointmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Appointments
        fields = "__all__"


class SalesmenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Salesmen
        fields = "__all__"


class SlotSerializer(serializers.ModelSerializer):
    level = serializers.IntegerField(required=False, read_only=True, default=0)

    class Meta:
        model = models.OpenSlots
        fields = "__all__"  # or list the fields you want ['field1', 'field2', ...]


class BestSlotsSerializer(serializers.ModelSerializer):
    slot = SlotSerializer(read_only=True)

    class Meta:
        model = models.BestSlots
        fields = "__all__"  # or list the fields you want ['field1', 'field2', ...]


class SchedulerSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SchedulerSettings
        fields = "__all__"
