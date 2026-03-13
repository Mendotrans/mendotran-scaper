# Mendotran requester
import requests
import time

url = "https://owa.visionblo.com/api/mendoza/stops"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0",
    "Accept": "*/*",
    "Referer": "https://owa.visionblo.com/web/mendoza/",
    "Content-Type": "application/json",
    "Origin": "https://owa.visionblo.com"
}

# HACK: lat, lon, latSpan and lonSpan should change dynamically
mendotran_request_stops_header = {
    "platform":"web",
    "v": "",
    "lat":"-32.09676406635843",
    "lon":"-69.62585449218751",
    "latSpan":"4.8667193939577835",
    "lonSpan":"9.788818359375",
    "version":"1.0",
}


def main() :
    mendotran_request_stops(mendotran_request_stops_header)

def mendotran_request_stops(payload):
    r = requests.get(url, data = payload, headers = headers)
    print(r)
    return



if (__name__ == "__main__"):
    main()
