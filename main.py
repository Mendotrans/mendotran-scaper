# Mendotran requester
import stops as stops
import service as service
import json
import os


def main():
    if os.path.isfile("mendotran.db"):
        print("Found DB!")
        somethingelese()
        exit(0)

    print("No DB found!")
    json_services_data = stops.mendotran_request_services()
    json_stops_data = stops.mendotran_request_stops()
    r = stops.mendotran_generate_db(json_stops_data, json_services_data)
    r_formated = json.dumps(r, indent=4)
    print(r_formated)


def somethingelese():
    r = service.mendotran_request_services(380375, True)
    r_formated = json.dumps(r, indent=4)
    print(r_formated)


if __name__ == "__main__":
    main()
