import tinytuya, requests, json, os
from datetime import datetime, timezone, timedelta
import gspread
from google.oauth2.service_account import Credentials

DEV = "eb0238bf2ba8be7e86npyl"
WID = "ITAIAU3"
WKY = "vqz5PM0x"
WCID = "2ef92e45844e22d8"
WCKY = "8da6e250dcd655ef52771d1975e29b14"
SHEET_ID = os.environ["SHEET_ID"]

c = tinytuya.Cloud(
    apiRegion="us",
    apiKey="scd8n7dxm74yarxvfjgg",
    apiSecret="5486c3b4c40844ddabb1adad1b9a2d06",
    apiDeviceID=DEV
)

r = c.getstatus(DEV)
d = {i["code"]: i["value"] for i in r["result"]}

temp_c   = d["temp_current_external"] / 10
temp_f   = round(temp_c * 9/5 + 32, 1)
hum      = d["humidity_outdoor"]
wind_kmh = d["windspeed_avg"] / 10
gust_kmh = d["windspeed_gust"] / 10
wind     = round(wind_kmh * 0.621371, 1)
gust     = round(gust_kmh * 0.621371, 1)
rain_h_mm  = d["rain_1h"] / 10
rain_24_mm = d["rain_24h"] / 10
rain_h   = round(rain_h_mm * 0.0393701, 3)
rain_d   = round(rain_24_mm * 0.0393701, 3)
press_hpa = d["atmospheric_pressture"]
press    = round(press_hpa * 0.02953, 2)
uv       = d["uv_index"]
dew_f    = round(d["dew_point_temp"] / 10 * 9/5 + 32, 1)

# ── Weather Underground ──
url = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"
params = {
    "ID": WID, "PASSWORD": WKY, "action": "updateraw", "dateutc": "now",
    "tempf": temp_f, "humidity": hum, "windspeedmph": wind,
    "windgustmph": gust, "rainin": rain_h, "dailyrainin": rain_d,
    "baromin": press, "UV": uv, "dewptf": dew_f
}
resp = requests.get(url, params=params)
print("WU:", resp.text)

# ── Weathercloud ──
wc_params = {
    "wid": WCID, "key": WCKY,
    "temp": d["temp_current_external"],
    "hum": hum,
    "wspd": d["windspeed_avg"],
    "wspdhi": d["windspeed_gust"],
    "wdir": d.get("wind_direction", 0),
    "rain": d["rain_1h"],
    "bar": round(press_hpa * 10),
    "uvi": uv,
    "dew": d["dew_point_temp"]
}
wc = requests.get("https://api.weathercloud.net/v01/set", params=wc_params)
print("Weathercloud:", wc.text)

print(f"Temp: {temp_f}F | Hum: {hum}% | Press: {press}inHg | UV: {uv} | Rain1h: {rain_h}in | Gust: {gust}mph")

# ── Google Sheets ──
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("gcreds.json", scopes=scopes)
gc = gspread.authorize(creds)
sh = gc.open_by_key(SHEET_ID)

estado = sh.worksheet("Estado do Dia")
resumo = sh.worksheet("Resumo Diário")

tz = timezone(timedelta(hours=-3))
today_str = datetime.now(tz).strftime("%d/%m/%Y")

ESTADO_HEADERS = ["Data","Temp Max (C)","Temp Min (C)","Pressao Max (hPa)","Pressao Min (hPa)","Chuva do Dia (mm)","Vento Soma","Vento Contagem","UV Max"]
RESUMO_HEADERS = ["Data","Temp Max (C)","Temp Min (C)","Pressao Max (hPa)","Pressao Min (hPa)","Chuva Total (mm)","Vento Medio (km/h)","UV Max"]

values = estado.get_all_values()

if not values or values[0] != ESTADO_HEADERS:
    estado.update(range_name="A1:I1", values=[ESTADO_HEADERS])
    resumo.update(range_name="A1:H1", values=[RESUMO_HEADERS])
    values = estado.get_all_values()

if len(values) < 2:
    estado.update(range_name="A2:I2", values=[[today_str, temp_c, temp_c, press_hpa, press_hpa, rain_24_mm, wind_kmh, 1, uv]])
else:
    row = values[1]
    saved_date = row[0]
    t_max, t_min, p_max, p_min, chuva, v_soma, v_cont, uv_max = [float(x) for x in row[1:9]]

    if saved_date != today_str:
        vento_medio = round(v_soma / v_cont, 1) if v_cont else 0
        resumo.append_row([saved_date, t_max, t_min, p_max, p_min, round(chuva,1), vento_medio, uv_max])
        estado.update(range_name="A2:I2", values=[[today_str, temp_c, temp_c, press_hpa, press_hpa, rain_24_mm, wind_kmh, 1, uv]])
    else:
        t_max = max(t_max, temp_c)
        t_min = min(t_min, temp_c)
        p_max = max(p_max, press_hpa)
        p_min = min(p_min, press_hpa)
        chuva = max(chuva, rain_24_mm)
        v_soma = v_soma + wind_kmh
        v_cont = v_cont + 1
        uv_max = max(uv_max, uv)
        estado.update(range_name="A2:I2", values=[[today_str, round(t_max,1), round(t_min,1), p_max, p_min, round(chuva,1), round(v_soma,1), v_cont, uv_max]])

print("Google Sheets atualizado!")

