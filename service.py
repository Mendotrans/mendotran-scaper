import requests

services_url = "https://owa.visionblo.com/api/mendoza/service"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "https://owa.visionblo.com/web/mendoza/",
    "Content-Type": "application/json",
    "Origin": "https://owa.visionblo.com",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Priority": "u=0",
    "TE": "trailers",
}


def mendotran_request_services(service_id: int, encoded_polyline: bool):
    payload = {
        "token": "OQkGfHEQqWRO9zXRQgJb",
        "service_id": service_id,
        "encode_polyline": encoded_polyline,
        "vehicles": True,
        "xss": "d50c19f185ed2a3535db18ec"
    }

    r = requests.post(services_url, json=payload, headers=headers)
    try:
        return r.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Request error, no json response, http error: {r.status_code}")
