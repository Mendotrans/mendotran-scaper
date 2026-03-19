import requests
import json
import sqlite3

stops_url = "https://owa.visionblo.com/api/mendoza/search"
stops_info_url = "https://owa.visionblo.com/api/mendoza/arrivals"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Accept": "*/*",
    "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
    "Content-Type": "application/json",
    "Origin": "https://owa.visionblo.com",
    "Referer": "https://owa.visionblo.com/web/mendoza/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}


def mendotran_request_stops():
    payload = {
        "token": "OQkGfHEQqWRO9zXRQgJb",
        "text": "",
        "xss": "86adb365fced6934d3ff6bec",
        "search": ["stops"],
        "no_favorites": True
    }
    r = requests.post(stops_url, json=payload, headers=headers)
    try:
        return r.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Request error, no json response, http error: {r.status_code}")


def mendotran_request_services():
    payload = {
        "token": "OQkGfHEQqWRO9zXRQgJb",
        "text": "",
        "xss": "86adb365fced6934d3ff6bec",
        "search": ["services"],
        "no_favorites": True
    }
    r = requests.post(stops_url, json=payload, headers=headers)
    try:
        return r.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Request error, no json response, http error: {r.status_code}")


def mendotran_generate_db(json_stops_data: json, json_services_data: json):
    print("Creating DB")
    with sqlite3.connect('mendotran.db') as connection:

        cursor = connection.cursor()

        create_table_querys = {}

        create_table_querys["stops"] = '''
        CREATE TABLE IF NOT EXISTS Stops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            stop_id INT NOT NULL,
            coordinate_lat REAL NOT NULL,
            coordinate_lon REAL NOT NULL,
            code TEXT,
            location TEXT
        );
        '''

        create_table_querys["services"] = '''
        CREATE TABLE IF NOT EXISTS Services(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            service_id INT NOT NULL,
            group_id INT NOT NULL,
            code TEXT,
            name TEXT,
            color TEXT,
            mode TEXT
        );
        '''

        create_table_querys["groups"] = '''
        CREATE TABLE IF NOT EXISTS Groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT,
            name TEXT
        );
        '''

        insert_querys = {}

        insert_querys["stops"] = '''
        INSERT INTO Stops
        (type, stop_id, coordinate_lat, coordinate_lon, code, location)
        VALUES
        (?, ?, ?, ?, ?, ?)
        '''

        insert_querys["services"] = '''
        INSERT INTO Services
        (type, service_id, group_id, code, name, color, mode)
        VALUES
        (?, ?, ?, ?, ?, ?, ?)
        '''

        insert_querys["groups"] = '''
        INSERT INTO Groups
        (group_id, name)
        VALUES
        (?, ?)
        '''

        for key, query in create_table_querys.items():
            res = cursor.execute(query)
            print(f"Created table: {res.fetchone()}")

        ##################################################################
        ########################### Stops Table ###########################
        ##################################################################
        print("Populating stops table")
        for stop in json_stops_data["search"]:
            insert_data = [
                str(stop["type"]),
                int(stop["stop_id"]),
                float(stop["coordinates"][0]),
                float(stop["coordinates"][1]),
                str(stop["code"]),
                str(stop["location"]),
            ]
            try:
                cursor.execute(insert_querys["stops"], insert_data)
            except sqlite3.OperationalError as e:
                print(f"Error inserting data: {e}")
                exit(1)

        ##################################################################
        ########################### Services Table ########################
        ##################################################################

        print("Populating services table")
        for stop in json_services_data["search"]:
            insert_data = [
                str(stop["type"]),
                int(stop["service_id"]),
                int(stop["group_id"]),
                str(stop["code"]),
                str(stop["name"]),
                str(stop["color"]),
                str(stop["mode"]),
            ]
            try:
                cursor.execute(insert_querys["services"], insert_data)
            except sqlite3.OperationalError as e:
                print(f"Error inserting data: {e}")
                exit(1)

        ##################################################################
        ########################### Groups Table ##########################
        ##################################################################
        print("Populating groups table")
        for group, name_dict in json_services_data["groups"].items():
            insert_data = [
                str(group),
                str(name_dict["name"]),

            ]
            try:
                cursor.execute(insert_querys["groups"], insert_data)
            except sqlite3.OperationalError as e:
                print(f"Error inserting data: {e}")
                exit(1)

        connection.commit()


def mendotran_request_stop_info(stop_id: int):
    payload = {
        "token": "OQkGfHEQqWRO9zXRQgJb",
        "stop_id": stop_id,
        "first_time": False,
        "xss": "0549a7684ade3d12e894d6df"
    }

    try:
        r = requests.post(stops_info_url, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.JSONDecodeError:
        print(f"No JSON response. Status code: {r.status_code}")
        print(f"Raw Response: {r.text}")
    return None
