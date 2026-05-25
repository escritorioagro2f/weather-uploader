import tinytuya
import requests
import json

DEV = "eb0238bf2ba8be7e86npyl"
WID = "ITAIAU3"
WKY = "vqz5PM0x"

c = tinytuya.Cloud(
    apiRegion="us",
    apiKey="scd8n7dxm74yarxvfjgg",
    apiSecret="5486c3b4c40844ddabb1adad1b9a2d06",
    apiDeviceID=DEV
)

result = c.getstatus(DEV)
print("DADOS:", json.dumps(result, indent=2))
