import requests, hashlib, hmac, time, json

TUYA_CLIENT_ID     = "scd8n7dxm74yarxvfjgg"
TUYA_CLIENT_SECRET = "5486c3b4c40844ddabb1adad1b9a2d06"
TUYA_DEVICE_ID     = "eb0238bf2ba8be7e86npyl"
TUYA_BASE_URL      = "https://openapi.tuyaus.com"

WU_STATION_ID  = "ITAIAU3"
WU_STATION_KEY = "vqz5PM0x"

def sign(secret, msg):
    return hmac.new(secret.encode("utf-8"), msg.encode("utf-8"), hashlib.sha256).hexdigest().upper()

def get_token():
    t = str(int(time.time() * 1000))
    string_to_sign = TUYA_CLIENT_ID + t
    headers = {
        "client_id":   TUYA_CLIENT_ID,
        "sign":        sign(TUYA_CLIENT_SECRET, string_to_sign),
        "t":           t,
        "sign_method": "HMAC-SHA256",
        "Content-Type": "application/json"
    }
    url = f"{TUYA_BASE_URL}/v1.0/token?grant_type=1"
    r = requests.get(url, headers=headers)
    print("TOKEN RESPOSTA COMPLETA:", r.text)
    resp = r.json()
    if not resp.get("success"):
        raise Exception(f"Erro token: {resp}")
    return resp["result"]["access_token"]

def get_status(token):
    t = str(int(time.time() * 1000))
    path = f"/v1.0/devices/{TUYA_DEVICE_ID}/status"
    string_to_sign = TUYA_CLIENT_ID + token + t + path
    headers = {
        "client_id":    TUYA_CLIENT_ID,
        "access_token": token,
        "sign":         sign(TUYA_CLIENT_SECRET, string_to_sign),
        "t":            t,
        "sign_method":  "HMAC-SHA256",
        "Content-Type": "application/json"
    }
    r = requests.get(f"{TUYA_BASE_URL}{path}", headers=headers)
    print("DEVICE RESPOSTA COMPLETA:", r.text)
    resp = r.json()
    if not resp.get("success"):
        raise Exception(f"Erro device: {resp}")
    data = {i["code"]: i["value"] for i in resp["result"]}
    print("Dados brutos:", json.dumps(data, indent=2))
    return data

def c_to_f(c): return round(c * 9/5 + 32, 1)
def ms_to_mph(ms): return round(ms * 2.23694, 1)
def mm_to_in(mm): return round(mm * 0.0393701, 3)
def hpa_to_inhg(hpa): return round(hpa *
