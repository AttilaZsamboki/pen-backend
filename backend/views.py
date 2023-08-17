from .utils.google_maps import get_street_view, get_street_view_url
from .utils.minicrm import update_adatlap_fields
import math
import codecs
from .utils.google_maps import calculate_distance
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from . import models
import json
from .utils.logs import log
from rest_framework import generics
from . import serializers

# Create your views here.

class CalculateDistance(APIView):
    def post(self, request):
        log("Penészmentesítés MiniCRM webhook meghívva",
            "INFO", "pen_calculate_distance")
        data = json.loads(str(request.body)[2:-1])["Data"]
        telephely = "Budapest, Nagytétényi út 218, 1225"

        address = f"{data['Cim2']} {data['Telepules']}, {data['Iranyitoszam']} {data['Orszag']}"
        gmaps_result = calculate_distance(
            start=telephely, end=codecs.unicode_escape_decode(address)[0])
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
            get_street_view(location=address)
        except Exception as e:
            log("Penészmentesítés MiniCRM webhook sikertelen", "FAILED", e)
        street_view_url = get_street_view_url(location=address)
        response = update_adatlap_fields(data["Id"], {
            "IngatlanKepe": "https://www.dataupload.xyz/static/images/google_street_view/street_view.jpg", "UtazasiIdoKozponttol": formatted_duration, "Tavolsag": distance, "FelmeresiDij": fee, "StreetViewUrl": street_view_url, "BruttoFelmeresiDij": round(fee*1.27)})
        if response.code == 200:
            log("Penészmentesítés MiniCRM webhook sikeresen lefutott",
                "SUCCESS", "pen_calculate_distance")
        else:
            log("Penészmentesítés MiniCRM webhook sikertelen",
                "ERROR", response.reason)
        return Response({'status': 'success'}, status=HTTP_200_OK)


class GoogleSheetWebhook(APIView):
    def post(self, request):
        data = json.loads(request.body)
        log("Penészmentesítés Google Sheets webhook meghívva", "INFO", "pen_google_sheet_webhook", json.dumps(data, indent=4))
        [models.Felmeresek(field=j, value=k["response"], adatlap_id=data["Adatlap hash (ne módosítsd!!)"]["response"], type=k["type"], options=k["options"]).save() for j, k in data.items()]
        return Response("Succesfully received data", status=HTTP_200_OK)

class FelmeresekList(generics.ListCreateAPIView):
    queryset = models.Felmeresek.objects.all()
    serializer_class = serializers.FelemeresekSerializer

class FelmeresekDetail(APIView):
    def get(self, request, id):
        felmeres = models.Felmeresek.objects.filter(adatlap_id=id)
        serializer = serializers.FelemeresekSerializer(felmeres, many=True)
        return Response(serializer.data)
