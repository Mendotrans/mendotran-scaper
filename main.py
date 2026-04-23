#!/usr/bin/env python3
"""
Mendotran CLI - Query Mendoza public transit data.
Usage: python mendotran_cli.py --help
"""

import argparse
import json
import os
import sqlite3
import time

import requests

# ── API constants ────────────────────────────────────────────────────────────

BASE_URL = "https://owa.visionblo.com/api/mendoza"
TOKEN = "OQkGfHEQqWRO9zXRQgJb"
DB_PATH = "mendotran.db"

HEADERS = {
    "User-Agent":     "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Accept":         "*/*",
    "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
    "Content-Type":   "application/json",
    "Origin":         "https://owa.visionblo.com",
    "Referer":        "https://owa.visionblo.com/web/mendoza/",
}

# ── Low-level API helpers ────────────────────────────────────────────────────


def _post(endpoint: str, payload: dict) -> dict | None:
    url = f"{BASE_URL}/{endpoint}"
    try:
        r = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        print(f"[error] Request failed: {e}")
        return None
    except ValueError:
        print(f"[error] Non-JSON response from {endpoint}")
        return None


def api_fetch_stops() -> dict | None:
    return _post("search", {
        "token": TOKEN, "text": "", "xss": "86adb365fced6934d3ff6bec",
        "search": ["stops"], "no_favorites": True,
    })


def api_fetch_services_list() -> dict | None:
    return _post("search", {
        "token": TOKEN, "text": "", "xss": "86adb365fced6934d3ff6bec",
        "search": ["services"], "no_favorites": True,
    })


def api_fetch_stop_arrivals(stop_id: int) -> dict | None:
    return _post("arrivals", {
        "token": TOKEN, "stop_id": stop_id,
        "first_time": False, "xss": "0549a7684ade3d12e894d6df",
    })


def api_fetch_service_detail(service_id: int) -> dict | None:
    return _post("service", {
        "token": TOKEN, "service_id": service_id,
        "encode_polyline": True, "vehicles": True,
        "xss": "d50c19f185ed2a3535db18ec",
    })

# ── Database ─────────────────────────────────────────────────────────────────


def db_connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def db_init(stops_data: dict, services_data: dict) -> None:
    print("[db] Creating and populating database …")
    with db_connect() as con:
        cur = con.cursor()
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS Stops (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                type           TEXT    NOT NULL,
                stop_id        INT     NOT NULL,
                coordinate_lat REAL    NOT NULL,
                coordinate_lon REAL    NOT NULL,
                code           TEXT,
                location       TEXT
            );
            CREATE TABLE IF NOT EXISTS Services (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                type       TEXT NOT NULL,
                service_id INT  NOT NULL,
                group_id   INT  NOT NULL,
                code       TEXT,
                name       TEXT,
                color      TEXT,
                mode       TEXT
            );
            CREATE TABLE IF NOT EXISTS Groups (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT,
                name     TEXT
            );
            CREATE TABLE IF NOT EXISTS ServiceDetails (
                service_id  INT  PRIMARY KEY,
                fetched_at  TEXT NOT NULL,
                payload     TEXT NOT NULL
            );
        """)

        for s in stops_data["search"]:
            cur.execute(
                "INSERT INTO Stops (type,stop_id,coordinate_lat,coordinate_lon,code,location) VALUES (?,?,?,?,?,?)",
                (s["type"], s["stop_id"], s["coordinates"][0],
                 s["coordinates"][1], s["code"], s["location"]),
            )

        for s in services_data["search"]:
            cur.execute(
                "INSERT INTO Services (type,service_id,group_id,code,name,color,mode) VALUES (?,?,?,?,?,?,?)",
                (s["type"], s["service_id"], s["group_id"],
                 s["code"], s["name"], s["color"], s["mode"]),
            )

        for gid, meta in services_data["groups"].items():
            cur.execute(
                "INSERT INTO Groups (group_id,name) VALUES (?,?)", (gid, meta["name"]))

        con.commit()
    print("[db] Done.")


def db_exists() -> bool:
    return os.path.isfile(DB_PATH)


def db_get_all_service_ids() -> list[int]:
    with db_connect() as con:
        rows = con.execute("SELECT service_id FROM Services").fetchall()
    return [r[0] for r in rows]


def db_search_stops(query: str) -> list[tuple]:
    with db_connect() as con:
        rows = con.execute(
            "SELECT stop_id, code, location FROM Stops WHERE location LIKE ? OR code LIKE ? LIMIT 20",
            (f"%{query}%", f"%{query}%"),
        ).fetchall()
    return rows


def db_list_services(query: str = "") -> list[tuple]:
    with db_connect() as con:
        if query:
            rows = con.execute(
                "SELECT service_id, code, name, mode FROM Services WHERE name LIKE ? OR code LIKE ? LIMIT 30",
                (f"%{query}%", f"%{query}%"),
            ).fetchall()
        else:
            rows = con.execute(
                "SELECT service_id, code, name, mode FROM Services LIMIT 50"
            ).fetchall()
    return rows


def db_save_service_detail(service_id: int, payload: dict) -> None:
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    with db_connect() as con:
        con.execute(
            "INSERT OR REPLACE INTO ServiceDetails (service_id, fetched_at, payload) VALUES (?,?,?)",
            (service_id, ts, json.dumps(payload)),
        )
        con.commit()


def db_get_service_detail(service_id: int) -> dict | None:
    with db_connect() as con:
        row = con.execute(
            "SELECT payload FROM ServiceDetails WHERE service_id=?", (
                service_id,)
        ).fetchone()
    return json.loads(row[0]) if row else None

# ── CLI commands ──────────────────────────────────────────────────────────────


def cmd_init(_args) -> None:
    """Download stops & services and build the local DB."""
    if db_exists():
        print(
            f"[info] '{DB_PATH}' already exists. Delete it first to re-initialise.")
        return
    print("[api] Fetching stops …")
    stops_data = api_fetch_stops()
    print("[api] Fetching services …")
    services_data = api_fetch_services_list()
    if not stops_data or not services_data:
        print("[error] Could not fetch data. Aborting.")
        return
    db_init(stops_data, services_data)
    print(f"[ok] Database ready at '{DB_PATH}'.")


def cmd_stops(args) -> None:
    """Search stops by name / code."""
    _require_db()
    query = args.query or ""
    rows = db_search_stops(query)
    if not rows:
        print("No stops found.")
        return
    print(f"{'stop_id':<10} {'code':<10} location")
    print("-" * 60)
    for stop_id, code, location in rows:
        print(f"{stop_id:<10} {code:<10} {location}")


def cmd_services(args) -> None:
    """List / search services."""
    _require_db()
    rows = db_list_services(args.query or "")
    if not rows:
        print("No services found.")
        return
    print(f"{'service_id':<12} {'code':<8} {'mode':<8} name")
    print("-" * 60)
    for sid, code, name, mode in rows:
        print(f"{sid:<12} {code:<8} {mode:<8} {name}")


def cmd_arrivals(args) -> None:
    """Show upcoming arrivals for a stop."""
    data = api_fetch_stop_arrivals(args.stop_id)
    if not data:
        return
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    arrivals = data.get("arrivals") or data.get("data") or data
    if isinstance(arrivals, list):
        for a in arrivals:
            print(json.dumps(a, ensure_ascii=False))
    else:
        print(json.dumps(arrivals, indent=2, ensure_ascii=False))


def cmd_service_detail(args) -> None:
    """Show detail for a single service (uses cache if available)."""
    cached = db_get_service_detail(args.service_id) if db_exists() else None
    if cached and not args.force:
        print("[cache] Serving from local DB (use --force to refresh).")
        data = cached
    else:
        data = api_fetch_service_detail(args.service_id)
        if data and db_exists():
            db_save_service_detail(args.service_id, data)

    if data:
        print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_fetch_all(args) -> None:
    """
    Fetch details for every service in the DB with polite rate-limiting.

    Uses a delay between requests (default 0.5 s) so the server is never
    hammered. Already-cached services are skipped unless --force is passed.
    """
    _require_db()
    service_ids = db_get_all_service_ids()
    total = len(service_ids)
    print(f"[info] {total} services found. delay={
          args.delay}s, force={args.force}")

    skipped = fetched = errors = 0
    for i, sid in enumerate(service_ids, 1):
        # skip if already cached
        if not args.force and db_get_service_detail(sid):
            skipped += 1
            continue

        print(f"[{i}/{total}] Fetching service {sid} …", end=" ", flush=True)
        data = api_fetch_service_detail(sid)
        if data:
            db_save_service_detail(sid, data)
            fetched += 1
            print("ok")
        else:
            errors += 1
            print("FAILED")

        time.sleep(args.delay)

    print(f"\n[done] fetched={fetched}  skipped(cached)={
          skipped}  errors={errors}")

# ── Helpers ──────────────────────────────────────────────────────────────────


def _require_db() -> None:
    if not db_exists():
        print(f"[error] Database not found. Run:  python {
              os.path.basename(__file__)} init")
        raise SystemExit(1)

# ── Argument parser ──────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mendotran",
        description="Mendotran CLI — Mendoza public transit query tool",
    )
    sub = p.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # init
    sub.add_parser("init", help="Download data and create local DB (run once)")

    # stops
    sp = sub.add_parser("stops", help="Search stops by name or code")
    sp.add_argument("query", nargs="?", default="",
                    help="Search term (omit to list all)")

    # services
    sv = sub.add_parser(
        "services", help="List or search transit services/lines")
    sv.add_argument("query", nargs="?", default="", help="Search term")

    # arrivals
    ar = sub.add_parser("arrivals", help="Live arrivals for a stop")
    ar.add_argument("stop_id", type=int,
                    help="Stop ID (get it from 'stops' command)")
    ar.add_argument("--json", action="store_true", help="Raw JSON output")

    # service-detail
    sd = sub.add_parser(
        "service-detail", help="Details + vehicle positions for a service")
    sd.add_argument("service_id", type=int,
                    help="Service ID (get it from 'services' command)")
    sd.add_argument("--force", action="store_true",
                    help="Ignore cache and re-fetch")

    # fetch-all
    fa = sub.add_parser(
        "fetch-all",
        help="Bulk-fetch all service details into the DB (rate-limited)",
    )
    fa.add_argument(
        "--delay", type=float, default=0.5, metavar="SECONDS",
        help="Pause between requests in seconds (default: 0.5)",
    )
    fa.add_argument("--force", action="store_true",
                    help="Re-fetch even if already cached")

    return p


COMMANDS = {
    "init":           cmd_init,
    "stops":          cmd_stops,
    "services":       cmd_services,
    "arrivals":       cmd_arrivals,
    "service-detail": cmd_service_detail,
    "fetch-all":      cmd_fetch_all,
}

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    COMMANDS[args.command](args)
