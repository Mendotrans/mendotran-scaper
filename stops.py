import requests

stops_url = "https://mendotran.oba.visionblo.com/oba_api/api/where/stops-for-location.json"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Referer": "https://mendotran.oba.visionblo.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


def mendotran_request_stops(params):
    r = requests.get(stops_url, params=params, headers=headers)
    return r
