import requests
import hashlib
import hmac
import time
import json

TUYA_CLIENT_ID = "scd8n7dxm74yarxvfjgg"
TUYA_CLIENT_SECRET = "5486c3b4c40844ddabb1adad1b9a2d06"
TUYA_DEVICE_ID = "eb0238bf2ba8be7e86npyl"
TUYA_BASE_URL = "https://openapi.tuyaus.com"

WU_STATION_ID = "ITAIAU3"
WU_STATION_KEY = "vqz5PM0x"


def sign(secret, msg):
    return hmac.new(
        secret.encode("utf-8"),
        msg.encode("utf-8"),
        hashlib.sha256
    ).hexdigest().upper()


def get_token():
    t = str(int(time.time() * 1000))
    string_to_sign = TUYA_CLIENT_ID + t
    headers = {
        "client_id": TUYA_CLIENT_ID,
        "sign": sign(TUYA_CLIENT_SECRET, string_to_sign),
        "t": t,
        "sign_method": "HMAC-SHA256",
        "Content-Type": "application/json"
    }
    url = TUYA_BASE_URL + "/v1.0/token?grant_type=1"
    r = requests.get(url, headers=headers)
    print("TOKEN RESPOSTA:", r.text)
    resp = r.json()
    if not resp.get("success"):
        raise Exception("Erro token: " + str(resp))
    return resp["result"]["access_token"]


def get_status(token):
    t = str(int(time.time() * 1000))
    path = "/v1.0/devices/" + TUYA_DEVICE_ID + "/status"
    string_to_sign = TUYA_CLIENT_ID + token + t + path
    headers = {
        "client_id": TUYA_CLIENT_ID,
        "access_token": token,
        "sign": sign(TUYA_CLIENT_SECRET, string_to_sign),
        "t": t,
        "sign_method": "HMAC-SHA256",
        "Content-Type": "application/json"
    }
    r = requests.get(TUYA_BASE_URL + path, headers=headers)
    print("DEVICE RESPOSTA:", r.text)
    resp = r.json()
    if not resp.get("success"):
        raise Exception("Erro device: " + str(resp))
    data = {}
    for item in resp["result"]:
        data[item["code"]] = item["value"]
    print("Dados:", json.dumps(data, indent=2))
    return data


def upload(data):
    temp_raw = data.get("temp_current", data.get("va_temperature", 0))
    hum = data.get("humidity_value", data.get("va_humidity", 0))
    wind_raw = data.get("wind_speed", 0)
    rain_raw = data.get("rain_hourly", data.get("rainfall", 0))
    press_raw = data.get("pressure_value", data.get("air_pressure", 0))

    temp_c = temp_raw / 10.0
    temp_f = round(temp_c * 9.0 / 5.0 + 32, 1)
    wind_mph = round((wind_raw / 10.0) * 2.23694, 1)
    rain_in = round((rain_raw / 10.0) * 0.0393701, 3)
    press_inhg = round((press_raw / 10.0) * 0.02953, 2)

    params = {
        "ID": WU_STATION_ID,
        "PASSWORD": WU_STATION_KEY,
        "tempf": temp_f,
        "humidity": hum,
        "windspeedmph": wind_mph,
    
