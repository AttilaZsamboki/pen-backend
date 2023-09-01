from .utils.google_maps import get_street_view, get_street_view_url
from .utils.minicrm import update_adatlap_fields, get_all_adatlap_details, list_to_dos, update_todo, statuses
from .utils.logs import log
from .utils.utils import delete_s3_file
from .utils.google_maps import calculate_distance

from . import models
from . import serializers

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_201_CREATED
from rest_framework.permissions import AllowAny
from rest_framework import generics

import json
import requests
import math
import codecs

# Create your views here.

class CalculateDistance(APIView):
    def post(self, request):
        data = json.loads(str(request.body)[2:-1])["Data"]
        log("Penészmentesítés MiniCRM webhook meghívva",
            "INFO", "pen_calculate_distance", json.dumps(data, indent=4))
        telephely = "Budapest, Nagytétényi út 218, 1225"

        address = f"{data['Cim2']} {data['Telepules']}, {data['Iranyitoszam']} {data['Orszag']}"
        gmaps_result = calculate_distance(
            start=telephely, end=codecs.unicode_escape_decode(address)[0])
        if gmaps_result == "Error":
            log("Penészmentesítés MiniCRM webhook sikertelen", "ERROR", "pen_calculate_distance",
                f"Hiba a Google Maps API-al való kommunikáció során {address}, adatlap id: {data['Id']}")
            return Response({'status': 'error'}, status=HTTP_200_OK)
        duration = gmaps_result["duration"] / 60
        distance = gmaps_result["distance"] // 1000
        formatted_duration = f"{math.floor(duration//60)} óra {math.floor(duration%60)} perc"
        fee_map = {
            0: 20000,
            31: 25000,
            101: 30000,
            201: 35000,
        }
        fee = fee_map[[i for i in fee_map.keys() if i < distance][-1]]

        try:
            get_street_view(location=codecs.unicode_escape_decode(address)[0])
        except Exception as e:
            log("Penészmentesítés MiniCRM webhook sikertelen", "FAILED", e)
        street_view_url = get_street_view_url(
            location=codecs.unicode_escape_decode(address)[0])
        response = update_adatlap_fields(data["Id"], {
            "IngatlanKepe": "https://www.dataupload.xyz/static/images/google_street_view/street_view.jpg", "UtazasiIdoKozponttol": formatted_duration, "Tavolsag": distance, "FelmeresiDij": fee, "StreetViewUrl": street_view_url, "BruttoFelmeresiDij": round(fee*1.27), "UtvonalAKozponttol": f"https://www.google.com/maps/dir/?api=1&origin=M%C3%A1tra+u.+17,+Budapest,+1224&destination={codecs.decode(address, 'unicode_escape')}&travelmode=driving"})
        if response.code == 200:
            log("Penészmentesítés MiniCRM webhook sikeresen lefutott",
                "SUCCESS", "pen_calculate_distance")
        else:
            log("Penészmentesítés MiniCRM webhook sikertelen",
                "ERROR", "pen_calculate_distance", response.reason)
        return Response({'status': 'success'}, status=HTTP_200_OK)

class GoogleSheetWebhook(APIView):
    def post(self, request):
        data = json.loads(request.body)
        urlap = data["Adatlap hash (ne módosítsd!!)"]["response"]
        log("Penészmentesítés Google Sheets webhook meghívva", "INFO", "pen_google_sheet_webhook", urlap)
        [models.FelmeresNotes(field=j, value=k["response"] if k["type"] not in ["GRID", "CHECKBOX_GRID", "FILE_UPLOAD", "CHECKBOX"] else json.dumps(k["response"], ensure_ascii=False), adatlap_id=urlap, type=k["type"], options=k["options"], section=k["section"]).save() for j, k in data.items()]
        requests.get("https://peneszmentesites.dataupload.xyz/api/revalidate?tag=felmeresek")
        requests.get(f"https://peneszmentesites.dataupload.xyz/api/revalidate?tag={data['Adatlap hash (ne módosítsd!!)']['response']}")
        def criteria(adatlap):
            return adatlap["ProjectHash"] == urlap
        adatlap_id = get_all_adatlap_details(category_id=23, criteria=criteria)[0]["Id"]
        update_adatlap_fields(adatlap_id, {"FelmeresAdatok": "https://peneszmentesites.dataupload.xyz/felmeresek/"+urlap, "StatusId": "Elszámolásra vár"})
        def todo_criteria(todo):
            return todo["Type"] == statuses["ToDo"]["Felmérés"] and todo["Status"] == "Open"
        todo_id = list_to_dos(adatlap_id, todo_criteria)[0]["Id"]
        update_todo(todo_id, {"Status": "Closed"})
        return Response("Succesfully received data", status=HTTP_200_OK)

class FelmeresQuestionsList(generics.ListCreateAPIView):
    queryset = models.FelmeresQuestions.objects.all()
    serializer_class = serializers.FelmeresQuestionsSerializer
    permission_classes = [AllowAny]

class FelmeresQuestionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.FelmeresQuestions.objects.all()
    serializer_class = serializers.FelmeresQuestionsSerializer

    def get(self, request, pk):
        felmeres = models.FelmeresQuestions.objects.filter(adatlap_id=pk)
        serializer = serializers.FelmeresQuestionsSerializer(felmeres, many=True)
        return Response(serializer.data)

class FelmeresekNotesList(generics.ListCreateAPIView):
    queryset = models.FelmeresNotes.objects.all()
    serializer_class = serializers.FelmeresekNotesSerializer
    permission_classes = [AllowAny]

class FelmeresekNotesDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.FelmeresNotes.objects.all()
    serializer_class = serializers.FelmeresekNotesSerializer
    permission_classes = [AllowAny]

    def delete(self, request, pk):
        note = models.FelmeresNotes.objects.get(pk=pk)
        if note:
            delete_s3_file(note.value)
            note.delete()
            return Response(status=HTTP_200_OK)
        else:
            return Response(status=HTTP_404_NOT_FOUND)

class OrderWebhook(APIView):
    def post(self, request):
        log("Penészmentesítés rendelés webhook meghívva", "INFO", "pen_order_webhook", request.body)
        return Response("Succesfully received data", status=HTTP_200_OK)

class ProductsList(generics.ListCreateAPIView):
    queryset = models.Products.objects.all()
    serializer_class = serializers.ProductsSerializer
    permission_classes = [AllowAny]

class ProductsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Products.objects.all()
    serializer_class = serializers.ProductsSerializer
    permission_classes = [AllowAny]

class ProductAttributesList(generics.ListCreateAPIView):
    queryset = models.ProductAttributes.objects.all()
    serializer_class = serializers.ProductAttributesSerializer
    permission_classes = [AllowAny]

class ProductAttributesDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.ProductAttributes.objects.all()
    serializer_class = serializers.ProductAttributesSerializer
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        product_attributes = models.ProductAttributes.objects.filter(product_id=pk)
        serializer = serializers.ProductAttributesSerializer(product_attributes, many=True)
        return Response(serializer.data)

class FiltersList(generics.ListCreateAPIView):
    queryset = models.Filters.objects.all()
    serializer_class = serializers.FiltersSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.query_params.get('type'):
            return models.Filters.objects.filter(type=self.request.query_params.get('type'))
        return super().get_queryset()

class FiltersDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Filters.objects.all()
    serializer_class = serializers.FiltersSerializer
    permission_classes = [AllowAny]

class QuestionsList(generics.ListCreateAPIView):
    queryset = models.Questions.objects.all()
    serializer_class = serializers.QuestionsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.query_params.get('product'):
            return models.Questions.objects.filter(product=self.request.query_params.get('product'))
        elif self.request.query_params.get("connection"):
            return models.Questions.objects.filter(connection=self.request.query_params.get('connection'))
        return super().get_queryset()

class QuestionsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Questions.objects.all()
    serializer_class = serializers.QuestionsSerializer
    permission_classes = [AllowAny]

class TemplateSerializerList(generics.ListCreateAPIView):
    queryset = models.Templates.objects.all()
    serializer_class = serializers.TemplatesSerializer
    permission_classes = [AllowAny]

class TemplateSerializerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Templates.objects.all()
    serializer_class = serializers.TemplatesSerializer
    permission_classes = [AllowAny]

class ProductTemplateSerializerList(generics.ListCreateAPIView):
    queryset = models.ProductTemplate.objects.all()
    serializer_class = serializers.ProductTemplateSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        template_id = request.data["template_id"]
        product_id = request.data["product_id"]
        template_instance = models.Templates.objects.get(id=template_id)
        product_instance = models.Products.objects.get(id=product_id)

        new_product_template = models.ProductTemplate(template=template_instance, product=product_instance)
        new_product_template.save()
        return Response(status=HTTP_200_OK)

    def put(self, request):
        template_id = self.request.query_params.get("template_id")
        products = models.ProductTemplate.objects.filter(template=template_id)
        products.delete()
        models.ProductTemplate.objects.bulk_create([models.ProductTemplate(template=models.Templates.objects.get(id=template_id), product=models.Products.objects.get(id=i)) for i in request.data])
        return Response(status=HTTP_200_OK)


class ProductTemplateSerializerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.ProductTemplate.objects.all()
    serializer_class = serializers.ProductTemplateSerializer
    permission_classes = [AllowAny]

    def get(self, request, pk):
        product_templates = models.ProductTemplate.objects.filter(template=pk)
        serializer = serializers.ProductTemplateSerializer(product_templates, many=True)
        return Response(serializer.data)

class FelmeresekList(generics.ListCreateAPIView):
    queryset = models.Felmeresek.objects.all()
    serializer_class = serializers.FelmeresekSerializer
    permission_classes = [AllowAny]

class FelmeresekDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Felmeresek.objects.all()
    serializer_class = serializers.FelmeresekSerializer
    permission_classes = [AllowAny]

class FelmeresItemsList(generics.ListCreateAPIView):
    queryset = models.FelmeresItems.objects.all()
    serializer_class = serializers.FelmeresItemsSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
    
    def get(self, request):
        if request.query_params.get("adatlap_id"):
            felmeres_items = models.FelmeresItems.objects.filter(adatlap_id=request.query_params.get("adatlap_id"))
            serializer = serializers.FelmeresItemsSerializer(felmeres_items, many=True)
            return Response(serializer.data)
        return super().get(request)

class FelmeresItemsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.FelmeresItems.objects.all()
    serializer_class = serializers.FelmeresItemsSerializer
    permission_classes = [AllowAny]