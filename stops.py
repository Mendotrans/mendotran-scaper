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


def mendotran_request_stop_info(stop_id: str):
    payload = {
        "first_time": "true",
        "stop_id": stop_id,
        "token": "OQkGfHEQqWRO9zXRQgJb",
        "xss": "3b935fa2ffe3c87bc65363e2",
    }
    r = requests.post(stops_info_url, json=payload, headers=headers)
    try:
        return r.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Request error, no json response, http error: {r.status_code}")


def mendotran_generate_stops_db(json_data: json):
    with sqlite3.connect('stops.db') as connection:

        cursor = connection.cursor()

        create_table_query = '''
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
        cursor.execute(create_table_query)

        insert_query = '''
        INSERT INTO Stops
        (type, stop_id, coordinate_lat, coordinate_lon, code, location)
        VALUES
        (?, ?, ?, ?, ?, ?)
        '''

        stops_list = json_data["search"][0]
        print(stops_list)

        for stop in json_data["search"]:
            insert_data = [
                str(stop["type"]),
                int(stop["stop_id"]),
                float(stop["coordinates"][0]),
                float(stop["coordinates"][1]),
                str(stop["code"]),
                str(stop["location"]),
            ]
            for data in insert_data:
                print(data)
            try:
                cursor.execute(insert_query, insert_data)
            except sqlite3.OperationalError as e:
                print(f"Error inserting data: {e}")
                exit(1)
            break

        connection.commit()
