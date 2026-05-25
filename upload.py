import requests, hashlib, hmac, time, json

CID = "scd8n7dxm74yarxvfjgg"
SEC = "5486c3b4c40844ddabb1adad1b9a2d06"
DEV = "eb0238bf2ba8be7e86npyl"
URL = "https://openapi.tuyaus.com"
WID = "ITAIAU3"
WKY = "vqz5PM0x"

def sg(msg):
    return hmac.new(SEC.encode(), msg.encode(), hashlib.sha256).hexdigest().upper()

def token():
    t = str(int(time.time()*1000))
    h = {"client_id":CID,"sign":sg(CID+t),"t":t,"sign_method":"HMAC-SHA256"}
    r = requests.get(URL+"/v1.0/token?grant_type=1", headers=h)
    print("TOKEN:", r.text)
    return r.json()["result"]["access_token"]

def status(tk):
    t = str(int(time.time()*1000))
    p = "/v1.0/devices/"+DEV+"/status"
    h = {"client_id":CID,"access_token":tk,"sign":sg(CID+tk+t+p),"t":t,"sign_method":"HMAC-SHA256"}
    r = requests.get(URL+p, headers=h)
    print("STATUS:", r.text)
    d = {i["code"]:i["value"] for i in r.json()["result"]}
    return d

tk = token()
d = status(tk)
print("DADOS:", json.dumps(d, indent=2))
