import requests, hashlib, hmac, time, json, os

TUYA_CLIENT_ID     = "scd8n7dxm74yarxvfjgg"
TUYA_CLIENT_SECRET = "5486c3b4c40844ddabb1adad1b9a2d06"
TUYA_DEVICE_ID     = "eb0238bf2ba8be7e86npyl"
TUYA_BASE_URL      = "https://openapi.tuyaus.com"

WU_STATION_ID  = "ITAIAU3"
WU_STATION_KEY = "vqz5PM0x"

def get_token():
    t = str(int(time.time() * 1000))
    msg = TUYA_CLIENT_ID + t
    sign = hmac.new(TUYA_CLIENT_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest().upper()
    r = requests.get(f"{TUYA_BASE_URL}/v1.0/token?grant_type=1", headers={
        "client_id": TUYA_CLIENT_ID, "sign": sign, "t": t, "sign_method": "HMAC-SHA256"
    })
    return r.json()["result"]["access_token"]

def get_status(token):
    t = str(int(time.time() * 1000))
    path = f"/v1.0/devices/{TUYA_DEVICE_ID}/status"
    msg = TUYA_CLIENT_ID + token + t + path
    sign = hmac.new(TUYA_CLIENT_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest().upper()
    r = requests.get(f"{TUYA_BASE_URL}{path}", headers={
        "client_id": TUYA_CLIENT_ID, "access_token": token,
        "sign": sign, "t": t, "sign_method": "HMAC-SHA256"
    })
    data = {i["code"]: i["value"] for i in r.json().get("result", [])}
    print("Dados brutos:", json.dumps(data, indent=2))
    return data

def c_to_f(c): return round(c * 9/5 + 32, 1)
def ms_to_mph(ms): return round(ms * 2.23694, 1)
def mm_to_in(mm): return round(mm * 0.0393701, 3)
def hpa_to_inhg(hpa): return round(hpa * 0.02953, 2)

def upload(data):
    temp   = data.get("temp_current", data.get("va_temperature", 0)) / 10
    hum    = data.get("humidity_value", data.get("va_humidity", 0))
    wind   = data.get("wind_speed", 0) / 10
    rain   = data.get("rain_hourly", data.get("rainfall", 0)) / 10
    press  = data.get("pressure_value", data.get("air_pressure", 0)) / 10

    params = {
        "ID": WU_STATION_ID, "PASSWORD": WU_STATION_KEY,
        "tempf": c_to_f(temp), "humidity": hum,
        "windspeedmph": ms_to_mph(wind),
        "rainin": mm_to_in(rain),
        "baromin": hpa_to_inhg(press),
        "dateutc": "now", "action": "updateraw"
    }
    r = requests.get("https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php", params=params)
    print(f"WU resposta: {r.text}")
    print(f"Temp: {params['tempf']}°F | Hum: {hum}% | Vento: {params['windspeedmph']}mph")

token = get_token()
status = get_status(token)
upload(status)
