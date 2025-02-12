import requests
import openrouteservice
import xml.etree.ElementTree as ET
from geopy.distance import geodesic
import os

API_REQUEST_HEADER = {"User-Agent": "VoltWay/1.0"}
ORS_API_KEY = os.getenv("ORS_API_KEY", "NONE")
SOAP_API = os.getenv("SOAP_API", "http://127.0.0.1:7000/get_time_cost")

def get_lat_lon(location):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location, "format": "json", "limit": 1}
    response = requests.get(url, params=params, headers=API_REQUEST_HEADER)
    if response.status_code == 200:
        return {"lat": float(response.json()[0]["lat"]), "lon": float(response.json()[0]["lon"])}
    return None

def get_waypoints(origin, destination):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    params = {"api_key": ORS_API_KEY, "start": f"{origin['lon']},{origin['lat']}", "end": f"{destination['lon']},{destination['lat']}"}
    response = requests.get(url, params=params, headers=API_REQUEST_HEADER)
    return response.json()["features"][0]["geometry"]["coordinates"] if response.status_code == 200 else None

def get_charging_stations_trip(waypoints, autonomy):
    distance = 0
    autonomy = int(autonomy) * 1000 - 1500
    charging_stations = []
    for i in range(len(waypoints) - 2):
        distance += geodesic((waypoints[i][1], waypoints[i][0]), (waypoints[i+1][1], waypoints[i+1][0])).meters
        if distance >= autonomy:
            closest_station = find_closest_charging_stations({"lat": waypoints[i][1], "lon": waypoints[i][0]})
            if closest_station:
                charging_stations.append(closest_station)
            distance = 0
    return charging_stations

def find_closest_charging_stations(point):
    url = "https://public.opendatasoft.com/api/records/1.0/search"
    params = {"geofilter.distance": f"{point['lat']},{point['lon']},20000", "dataset": "osm-france-charging-station"}
    response = requests.get(url, params=params, headers=API_REQUEST_HEADER)
    stations = response.json().get('records', []) if response.status_code == 200 else []
    return stations[0]["geometry"]["coordinates"] if stations else None

def get_full_trip(waypoints):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    json_payload = {"coordinates": waypoints}
    response = requests.post(url, json=json_payload, headers=API_REQUEST_HEADER, params={"api_key": ORS_API_KEY})
    if response.status_code == 200:
        data = response.json()
        return {"bbox": data["bbox"], "summary": data["routes"][0]["summary"], "waypoints": openrouteservice.convert.decode_polyline(data["routes"][0]["geometry"])["coordinates"]}
    return None

def add_charging(trip, loadTime, autonomy):
    headers = {"Content-Type": "text/xml; charset=utf-8"}
    soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="voltway.soap">
        <soap:Header/>
        <soap:Body>
            <ns:get_time_cost>
                <ns:distance>{trip["summary"]["distance"]}</ns:distance>
                <ns:baseTime>{trip["summary"]["duration"]}</ns:baseTime>
                <ns:loadTime>{loadTime}</ns:loadTime>
                <ns:autonomy>{autonomy}</ns:autonomy>
            </ns:get_time_cost>
        </soap:Body>
    </soap:Envelope>"""
    response = requests.post(SOAP_API, data=soap_body, headers=headers)
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        namespace = {'tns': 'voltway.soap'}
        time_elem, cost_elem = root.find(".//tns:time", namespace), root.find(".//tns:cost", namespace)
        if time_elem is not None and cost_elem is not None:
            trip["summary"]["cost"] = float(cost_elem.text)
            trip["summary"]["duration"] = float(time_elem.text)
    return trip
