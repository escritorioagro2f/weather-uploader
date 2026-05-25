import tinytuya, requests, json

DEV = "eb0238bf2ba8be7e86npyl"
WID = "ITAIAU3"
WKY = "vqz5PM0x"
WCID = "2ef92e45844e22d8"
WCKY = "8da6e250dcd655ef52771d1975e29b14"

c = tinytuya.Cloud(
    apiRegion="us",
    apiKey="scd8n7dxm74yarxvfjgg",
    apiSecret="5486c3b4c40844ddabb1adad1b9a2d06",
    apiDeviceID=DEV
)

r = c.getstatus(DEV)
d = {i["code"]: i["value"] for i in r["result"]}

temp_f  = round(d["temp_current_external"] / 10 * 9/5 + 32, 1)
hum     = d["humidity_outdoor"]
wind    = round(d["windspeed_avg"] * 0.621371, 1)
gust    = round(d["windspeed_gust"] * 0.621371, 1)
rain_h  = round(d["rain_1h"] * 0.0393701, 3)
rain_d  = round(d["rain_24h"] * 0.0393701, 3)
press   = round(d["atmospheric_pressture"] * 0.02953, 2)
uv      = d["uv_index"]
dew_f   = round(d["dew_point_temp"] / 10 * 9/5 + 32, 1)

url = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"
params = {
    "ID": WID, "PASSWORD": WKY, "action": "updateraw", "dateutc": "now",
    "tempf": temp_f, "humidity": hum, "windspeedmph": wind,
    "windgustmph": gust, "rainin": rain_h, "dailyrainin": rain_d,
    "baromin": press, "UV": uv, "dewptf": dew_f
}
wc_params = {
    "wid": WCID, "key": WCKY,
    "temp": round(d["temp_current_external"]/10, 1),
    "hum": hum,
    "wspd": round(d["windspeed_avg"]/10, 1),
    "wspdhi": round(d["windspeed_gust"]/10, 1),
    "wdir": d.get("wind_direction", 0),
    "rain": round(d["rain_1h"]/10, 1),
    "bar": round(d["atmospheric_pressture"]/10, 1),
    "uvi": uv,
    "dew": round(d["dew_point_temp"]/10, 1)
}
}
wc = requests.get("https://api.weathercloud.net/v01/set", params=wc_params)
print("Weathercloud:", wc.text)
resp = requests.get(url, params=params)
print("WU:", resp.text)
print(f"Temp: {temp_f}F | Hum: {hum}% | Press: {press}inHg | UV: {uv}")


