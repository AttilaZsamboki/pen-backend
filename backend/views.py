from .utils.google_maps import get_street_view, get_street_view_url
from .utils.minicrm import update_adatlap_fields, get_all_adatlap_details, list_to_dos, update_todo, statuses, get_order, get_adatlap_details, contact_details, address_list, get_all_adatlap
from .utils.logs import log
from .utils.utils import delete_s3_file
from .utils.google_maps import calculate_distance

from . import models
from . import serializers

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED
from rest_framework.permissions import AllowAny
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import generics

from django.db import connection
from django.http import HttpResponse
from django.db.models import Q

import json
import requests
import math
import os
import random
import string
import datetime

import xml.etree.ElementTree as ET

# Create your views here.

class CalculateDistance(APIView):
    def post(self, request):
        log("Penészmentesítés MiniCRM webhook meghívva",
            "INFO", "pen_calculate_distance", request.body.decode("utf-8"))
        data = json.loads(request.body.decode("utf-8"))["Data"]
        telephely = "Budapest, Nagytétényi út 218-220, 1225"

        address = f"{data['Cim2']} {data['Telepules']}, {data['Iranyitoszam']} {data['Orszag']}"
        gmaps_result = calculate_distance(
            start=telephely, end=address)
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
            get_street_view(location=address[0])
        except Exception as e:
            log("Penészmentesítés MiniCRM webhook hiba", "FAILED", e)
        street_view_url = get_street_view_url(
            location=address)
        try:
            county = models.Counties.objects.get(telepules=data["Telepules"]).megye
        except:
            county = ""
            log(log_value="Penészmentesítés MiniCRM webhook sikertelen", status="FAILED", script_name="pen_calculate_distance", details=f"Nem található megye a településhez: {data['Telepules']}")
        response = update_adatlap_fields(data["Id"], {
            "IngatlanKepe": "https://www.dataupload.xyz/static/images/google_street_view/street_view.jpg", "UtazasiIdoKozponttol": formatted_duration, "Tavolsag": distance, "FelmeresiDij": fee, "StreetViewUrl": street_view_url, "BruttoFelmeresiDij": round(fee*1.27), "UtvonalAKozponttol": f"https://www.google.com/maps/dir/?api=1&origin=Nagytétényi+út+218,+Budapest,+1225&destination={address}&travelmode=driving", "Megye": county})
        if response["code"] == 200:
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
        data = json.loads(request.body)
        log("Penészmentesítés rendelés webhook meghívva", "INFO", "pen_order_webhook", data["Id"])
        try:
            models.Orders(adatlap_id=data["Id"], order_id=data["Head"]["Id"]).save()
        except Exception as e:
            log("Penészmentesítés rendelés webhook sikertelen", "ERROR", "pen_order_webhook", e)
            return
        log("Penészmentesítés rendelés webhook sikeresen lefutott", "SUCCESS", "pen_order_webhook")
        return Response("Succesfully received data", status=HTTP_200_OK)


class ProductsList(generics.ListCreateAPIView):
    serializer_class = serializers.ProductsSerializer
    permission_classes = [AllowAny]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        queryset = models.Products.objects.all()
        filter = self.request.query_params.get('filter', None)
        if filter is not None:
            filter_words = filter.split(" ")
            q_objects = Q()
    
            for word in filter_words:
                q_objects &= (
                    Q(id__icontains=word) |
                    Q(name__icontains=word) |
                    Q(sku__icontains=word) |
                    Q(type__icontains=word) |
                    Q(price_list_alapertelmezett_net_price_huf__icontains=word)
                    # Add more Q objects for each column you want to search
                )
    
            queryset = queryset.filter(q_objects)
    
        return queryset

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

class TemplateList(generics.ListCreateAPIView):
    queryset = models.Templates.objects.all()
    serializer_class = serializers.TemplatesSerializer
    permission_classes = [AllowAny]

class TemplateDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Templates.objects.all()
    serializer_class = serializers.TemplatesSerializer
    permission_classes = [AllowAny]

class ProductTemplatesList(generics.ListCreateAPIView):
    queryset = models.ProductTemplate.objects.all()
    serializer_class = serializers.ProductTemplateSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        data = json.loads(request.body)
        template_instance = models.Templates.objects.get(id=data["template_id"])
        product_instance = models.Products.objects.get(id=data["product_id"])

        models.ProductTemplate.objects.create(template=template_instance, product=product_instance)
        return Response(status=HTTP_200_OK)

    def put(self, request):
        template_id = self.request.query_params.get("template_id")
        products = models.ProductTemplate.objects.filter(template=template_id)
        products.delete()
        models.ProductTemplate.objects.bulk_create([models.ProductTemplate(template=models.Templates.objects.get(id=template_id), product=models.Products.objects.get(id=i)) for i in request.data])
        return Response(status=HTTP_200_OK)


class ProductTemplateDetail(generics.RetrieveUpdateDestroyAPIView):
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

class OfferWebhook(APIView):
    def post(self, request):
        log("Penészmentesítés rendelés webhook meghívva", "INFO", "pen_offer_webhook", request.body)
        data = json.loads(request.body)
        try:
            models.Offers(adatlap_id=data["Id"], offer_id=data["Head"]["Id"]).save()
            log("Penészmentesítés rendelés webhook sikeresen lefutott", "SUCCESS", "pen_offer_webhook")
        except Exception as e:
           log("Penészmentesítés rendelés webhook sikertelen", "ERROR", "pen_offer_webhook", e)
        return Response("Succesfully received data", status=HTTP_200_OK)

class QuestionProductsList(generics.ListCreateAPIView):
    queryset = models.QuestionProducts.objects.all()
    serializer_class = serializers.QuestionProductsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.query_params.get('product'):
            return models.QuestionProducts.objects.filter(product=self.request.query_params.get('product'))
        return super().get_queryset()

    def post(self, request):
        data = json.loads(request.body)
        print(data)
        question_instance = models.Questions.objects.get(id=data["question_id"])
        product_instance = models.Products.objects.get(id=data["product_id"])

        models.QuestionProducts.objects.create(question=question_instance, product=product_instance)
        return Response(status=HTTP_200_OK)

    def put(self, request):
        question_id = self.request.query_params.get("question_id")
        product_id = self.request.query_params.get("product")
        if question_id:
            products = models.QuestionProducts.objects.filter(question=question_id)
            products.delete()
            models.QuestionProducts.objects.bulk_create([models.QuestionProducts(question=models.Questions.objects.get(id=question_id), product=models.Products.objects.get(id=i)) for i in request.data])
            return Response(status=HTTP_200_OK)
        if product_id:
            questions = models.QuestionProducts.objects.filter(product=product_id)
            questions.delete()
            models.QuestionProducts.objects.bulk_create([models.QuestionProducts(question=models.Questions.objects.get(id=i), product=models.Products.objects.get(id=product_id)) for i in request.data])
            return Response(status=HTTP_200_OK)

class QuestionProductsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.QuestionProducts.objects.all()
    serializer_class = serializers.QuestionProductsSerializer
    permission_classes = [AllowAny]

    def get(self, request, pk):
        question_products = models.QuestionProducts.objects.filter(question=pk)
        serializer = serializers.QuestionProductsSerializer(question_products, many=True)
        return Response(serializer.data)


class UnasLogin(APIView):
    def post(self, request):
        log("Unas login meghívva", "INFO", "pen_unas_login", request.body.decode("utf-8"))
        response = request.body.decode("utf-8")
        root = ET.fromstring(response)
        for element in root.iter('ApiKey'):
            api_key = element.text
            if api_key == os.environ.get("CLOUD_API_KEY"):
                Login = ET.Element('Login')
                Token = ET.SubElement(Login, 'Token')
                Token.text = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=32))
                with connection.cursor() as cursor:
                    cursor.execute("TRUNCATE pen_erp_auth_tokens")
                models.ErpAuthTokens(token=Token.text, expire=(datetime.datetime.now() + datetime.timedelta(days=365*2)).strftime("%Y-%m-%d %H:%M:%S")).save()
                
                Expire = ET.SubElement(Login, 'Expire')
                Expire.text = (datetime.datetime.now() + datetime.timedelta(days=365*2)).strftime("%Y.%m.%d %H:%M:%S")
                
                ShopId = ET.SubElement(Login, 'ShopId')
                ShopId.text = "119"

                Subscription = ET.SubElement(Login, 'Subscription')
                Subscription.text ="vip-100000"

                Permissions = ET.SubElement(Login,'Permissions')
                permission_items = ["getOrder"]
                for item in permission_items:
                    permission_sub = ET.SubElement(Permissions,'Permission')  
                    permission_sub.text = item

                Status = ET.SubElement(Login,'Status')
                Status.text = "ok"
                
                response = '<?xml version="1.0" encoding="UTF-8" ?>\n' + ET.tostring(Login,encoding='unicode')
                return HttpResponse(response, status=HTTP_200_OK)
            return Response("Hibás API kulcs", status=HTTP_401_UNAUTHORIZED)

class UnasGetOrder(APIView):
    def get(self, request):
        log("Unas rendelések lekérdezése meghívva", "INFO", "pen_unas_get_order", request.body.decode("utf-8"))
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            try:
                token = auth_header[7:]  # Extract the token
                token = models.ErpAuthTokens.objects.get(token=token)
                if token.expire > datetime.datetime.now():
                    datas = [{"OrderData": get_order(models.Orders.objects.get(adatlap_id=i["Id"]).order_id), "AdatlapDetails": get_adatlap_details(id=i["Id"]), "BusinessKapcsolat": contact_details(contact_id=i["BusinessId"]), "Cím": address_list(i["BusinessId"])[0], "Kapcsolat": contact_details(contact_id=i["ContactId"])} for i in get_all_adatlap(category_id=29, status_id=3008)["Results"].values() if get_all_adatlap(category_id=29, status_id=3008)["Results"] != {}]
                    response = """<?xml version="1.0" encoding="UTF-8" ?>
                    <Orders> """ + "\n".join([f"""<Order>
                            <Key>{data["OrderData"]["Id"]}</Key>
                            <Date>{data["AdatlapDetails"]["CreatedAt"]}</Date>
                            <DateMod>{data["AdatlapDetails"]["UpdatedAt"]}</DateMod>
                            <Lang>hu</Lang>
                            <Customer>
                                <Id>{data["Kapcsolat"]["Id"]}</Id>
                                <Email>{data["Kapcsolat"]["Email"]}</Email>
                                <Username>{data["Kapcsolat"]["LastName"] + " " + data["Kapcsolat"]["FirstName"]}</Username>
                                <Contact>
                                    <Name>{data["Kapcsolat"]["LastName"] + " " + data["Kapcsolat"]["FirstName"]}</Name>
                                    <Phone>{data["Kapcsolat"]["Phone"]}</Phone>
                                    <Mobile>{data["Kapcsolat"]["Phone"]}</Mobile>
                                    <Lang>hu</Lang>
                                </Contact>
                                <Addresses>
                                    <Invoice>
                                        <Name>{data["BusinessKapcsolat"]["Name"]}</Name>
                                        <ZIP>{data["Cím"]["PostalCode"]}</ZIP>
                                        <City>{data["Cím"]["City"]}</City>
                                        <Street>{data["Cím"]["Address"]}</Street>
                                        <StreetName>{data["Cím"]["Address"].split(" ")[0]}</StreetName>
                                        <StreetType>{data["Cím"]["Address"].split(" ")[1]}</StreetType>
                                        <StreetNumber>{data["Cím"]["Address"].split(" ")[2]}</StreetNumber>
                                        <County>{data["Cím"]["County"]}</County>
                                        <Country>{data["Cím"]["CountryId"]}</Country>
                                        <CountryCode>hu</CountryCode>
                                        <TaxNumber>{data["BusinessKapcsolat"]["VatNumber"]}</TaxNumber>
                                        <EUTaxNumber>{data['BusinessKapcsolat']["EUVatNumber"] if data['BusinessKapcsolat']["EUVatNumber"] else ""}</EUTaxNumber>
                                        <CustomerType>private</CustomerType>
                                    </Invoice>
                                    <Shipping>
                                        <Name>{data['OrderData']["Customer"]["Name"]}</Name>
                                        <ZIP>{data['OrderData']["Customer"]["PostalCode"]}</ZIP>
                                        <City>{data["OrderData"]["Customer"]["City"]}</City>
                                        <Street>{data["OrderData"]["Customer"]["Address"]}</Street>
                                        <StreetName>{data["OrderData"]["Customer"]["Address"].split(" ")[0]}</StreetName>
                                        <StreetType>{data["OrderData"]["Customer"]["Address"].split(" ")[1]}</StreetType>
                                        <StreetNumber>{data["OrderData"]["Customer"]["Address"].split(" ")[2]}</StreetNumber>
                                        <County>{data["OrderData"]["Customer"]["County"]}</County>
                                        <Country>{data["OrderData"]["Customer"]["CountryId"]}</Country>
                                        <CountryCode>hu</CountryCode>
                                        <DeliveryPointID>6087-NOGROUPGRP</DeliveryPointID>
                                        <DeliveryPointGroup>gls_hu_dropoffpoints</DeliveryPointGroup>
                                        <RecipientName>{data["OrderData"]["Customer"]["Name"]}</RecipientName>
                                    </Shipping>
                                </Addresses>
                            </Customer>
                            <Currency>{data['OrderData']["CurrencyCode"]}</Currency>
                            <Status>Folyamatban</Status>
                            <StatusDateMod><![CDATA[2021.03.25 20:15:39]]></StatusDateMod>
                            <StatusID>3008</StatusID>
                            <Payment>
                                <Id>3338656</Id>
                                <Name>{data["OrderData"]["PaymentMethod"]}</Name>
                                <Type>transfer</Type>
                            </Payment>
                            <Shipping>
                                <Id>3372937</Id>
                                <Name><![CDATA[GLS CsomagPontok]]></Name>
                            </Shipping>
                            <SumPriceGross>{sum([float(i["PriceTotal"]) for i in data["OrderData"]["Items"]])}</SumPriceGross>
                            <Items>
                                """+"\n".join([f"""<Item>
                                    <Id>{i["Id"]}</Id>
                                    <Sku>{i["SKU"]}</Sku>
                                    <Name>{i["Name"]}</Name>
                                    <ProductParams>
                                    </ProductParams>
                                    <Unit>{i["Unit"]}</Unit>
                                    <Quantity>{i["Quantity"]}</Quantity>
                                    <PriceNet>{i["PriceNet"]}</PriceNet>
                                    <PriceGross>{float(i["PriceNet"])*1.27}</PriceGross>
                                    <Vat>{i["VAT"]}</Vat>
                                    <Status>
                                        <![CDATA[]]>
                                    </Status>
                                    </Item>
                                    """ for i in data["OrderData"]["Items"]])+"""
                            </Items>
                        </Order> """ for data in datas]) + """
                        </Orders>
                    """
                    return HttpResponse(response, status=HTTP_200_OK)
                else:
                    return Response("Token lejárt", status=HTTP_401_UNAUTHORIZED)
            except Exception as e:
                return Response("Hibás Token", status=HTTP_401_UNAUTHORIZED)
        return Response("Hibás Token", status=HTTP_401_UNAUTHORIZED)