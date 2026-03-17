# Mendotran requester
import stops as stops
import json


def main():
    #    r = stops.mendotran_request_stop_info(25600)
    r = stops.mendotran_request_stops()
    stops.mendotran_generate_stops_db(r)


if __name__ == "__main__":
    main()
