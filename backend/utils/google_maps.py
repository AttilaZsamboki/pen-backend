import requests
import os
import googlemaps
import dotenv
import traceback

from .logs import log
from .utils import base_path

dotenv.load_dotenv()


def calculate_distance(start, end, mode="driving", waypoints=None, priorty="duration"):
    gmaps = googlemaps.Client(key=os.environ.get("GOOGLE_MAPS_API_KEY"))
    try:
        direction_result = gmaps.directions(
            start, end, mode=mode, alternatives=True, waypoints=waypoints
        )
    except (googlemaps.exceptions.ApiError, googlemaps.exceptions.HTTPError) as e:
        log(
            "Hiba a Google Maps API-al való kommunikáció során",
            status="ERROR",
            script_name="pen_calculate_distance",
            details=e,
        )
        return traceback.format_exc()
    if not direction_result:
        log(
            "Hiba a Google Maps API-al való kommunikáció során. Hibásan megadott cím",
            status="INFO",
            script_name="pen_calculate_distance",
            details=f"start: {start}, end: {end}, mode: {mode}, waypoints: {waypoints}",
        )
        return
    if priorty == "distance":
        if waypoints:
            distance = min(
                [
                    sum(
                        [
                            i["legs"][j]["distance"]["value"]
                            for j in range(len(i["legs"]))
                        ]
                    )
                    for i in direction_result
                ]
            )
            duration = sum(
                [
                    i
                    for i in direction_result
                    if sum(
                        [
                            i["legs"][j]["distance"]["value"]
                            for j in range(len(i["legs"]))
                        ]
                    )
                    == distance
                ][0]["legs"][j]["duration"]["value"]
                for j in range(len(direction_result[0]["legs"]))
            )
        else:
            distance = min(
                [i["legs"][0]["distance"]["value"] for i in direction_result]
            )
            duration = [
                i
                for i in direction_result
                if i["legs"][0]["distance"]["value"] == distance
            ][0]["legs"][0]["duration"]["value"]
    elif priorty == "duration":
        if waypoints:
            duration = min(
                [
                    sum(
                        [
                            i["legs"][j]["duration"]["value"]
                            for j in range(len(i["legs"]))
                        ]
                    )
                    for i in direction_result
                ]
            )
            distance = sum(
                [
                    i
                    for i in direction_result
                    if sum(
                        [
                            i["legs"][j]["duration"]["value"]
                            for j in range(len(i["legs"]))
                        ]
                    )
                    == duration
                ][0]["legs"][j]["distance"]["value"]
                for j in range(len(direction_result[0]["legs"]))
            )
        else:
            duration = min(
                [i["legs"][0]["duration"]["value"] for i in direction_result]
            )
            distance = [
                i
                for i in direction_result
                if i["legs"][0]["duration"]["value"] == duration
            ][0]["legs"][0]["distance"]["value"]
    return {"distance": distance, "duration": duration}


def get_street_view(location):
    size = "1920x1080"
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    base_url = "https://maps.googleapis.com/maps/api/streetview"
    params = {"size": size, "location": location, "key": api_key}
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        # The request was successful, return the response
        if response.content is not None:
            with open(
                base_path + "/static/images/google_street_view/street_view.jpg", "wb"
            ) as img_file:
                img_file.write(response.content)
        return response
    else:
        return response


def get_street_view_url(location):
    # Use the Geocoding API to get the latitude and longitude
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": location, "key": api_key}
    response = requests.get(geocoding_url, params=params)
    response.raise_for_status()  # Raise an exception if the request failed
    result = response.json()

    if not result["results"]:
        log(
            "Hiba a Google Maps API-al való kommunikáció során. Hibásan megadott cím",
            status="INFO",
            script_name="get_street_view_url",
            details=location,
        )

    # Get the latitude and longitude from the first result
    lat_lng = result["results"][0]["geometry"]["location"]
    lat, lng = lat_lng["lat"], lat_lng["lng"]

    # Construct the Google Street View URL
    street_view_url = f"http://maps.google.com/?cbll={lat},{lng}&layer=c"

    return street_view_url
