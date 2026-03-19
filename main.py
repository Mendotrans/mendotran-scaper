# Mendotran requester
import stops as stops
import json


def main():
    json_services_data = stops.mendotran_request_services()
    json_stops_data = stops.mendotran_request_stops()
    r = stops.mendotran_generate_db(json_stops_data, json_services_data)
    r_formated = json.dumps(r, indent=4)
    print(r_formated)

    pass


if __name__ == "__main__":
    main()
