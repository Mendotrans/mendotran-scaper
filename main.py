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

mendotran_request_stops_header = {
}


def main() :
    mendotran_request_stops({})

def mendotran_request_stops(payload):
    r = requests.get(url, data = payload, headers = headers)
    print(r)
    return



if (__name__ == "__main__"):
    main()
