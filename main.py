# Mendotran requester
import stops as stops

# HACK: lat, lon, latSpan and lonSpan should change dynamically
mendotran_request_stops_params = {
    "platform": "web",
    "v": "",
    "lat": "",
    "lon": "",
    "latSpan": "",
    "lonSpan": "",
    "version": "1.0",
}


def make_stop_request_params(lat: float, lon: float, latSpan: float, lonSpan: float):
    params = dict(mendotran_request_stops_params)
    params["lat"] = str(lat)
    params["lon"] = str(lon)
    params["latSpan"] = str(latSpan)
    params["lonSpan"] = str(lonSpan)
    return params


def main():
    r = stops.mendotran_request_stops(
        make_stop_request_params(-32.74, -68.70, 0.37, 1.28))
    print(r.content)


if __name__ == "__main__":
    main()
