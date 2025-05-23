#!/usr/bin/env python3
import json
import datetime
import pytz
import swisseph as swe
import os
from timezonefinder import TimezoneFinder

APPLET_PATH = os.path.dirname(os.path.realpath(__file__))
NAIDHANA_START_FRACTION = 0.75
VIPAT_NAKSHATRAS = [2, 6, 10, 14, 18, 22, 26]

SCOPE_LETTERS = ["D", "K", "A", "M"]  # Dharma, Kama, Artha, Moksha

def read_config():
    config_path = os.path.join(APPLET_PATH, "config.json")
    with open(config_path, "r") as f:
        cfg = json.load(f)
    dt = datetime.datetime(cfg["year"], cfg["month"], cfg["day"], cfg["hour"], cfg["minute"])
    return dt, cfg["latitude"], cfg["longitude"]

def get_timezone(lat, lon, dt):
    tf = TimezoneFinder()
    tz_str = tf.timezone_at(lat=lat, lng=lon) or "UTC"
    return pytz.timezone(tz_str)

def to_utc(dt_local, tz):
    return tz.localize(dt_local).astimezone(pytz.utc)

def get_ayanamsa(jd):
    return swe.get_ayanamsa(jd)

def get_planet_longitudes(jd_ut):
    # Only get visible planets and manually label Rahu and Ketu
    visible_planets = [
        (swe.SUN, "Sun"),
        (swe.MOON, "Moon"),
        (swe.MARS, "Mars"),
        (swe.MERCURY, "Mercury"),
        (swe.JUPITER, "Jupiter"),
        (swe.VENUS, "Venus"),
        (swe.SATURN, "Saturn"),
        (swe.MEAN_NODE, "Rahu")  # Use Mean Node for Rahu
    ]
    
    longitudes = {}
    for p_id, name in visible_planets:
        lon = swe.calc_ut(jd_ut, p_id)[0][0]
        longitudes[name] = lon

    # Ketu is 180 degrees opposite Rahu
    longitudes["Ketu"] = (longitudes["Rahu"] + 180.0) % 360
    return longitudes

def get_lagna(jd_ut, lat, lon):
    return swe.houses(jd_ut, lat, lon)[0][0]

def get_house(planet_lon, asc):
    return int(((planet_lon - asc) % 360) // 30) + 1

def get_nakshatra_index(lon):
    return int(lon // 13.3333333), (lon % 13.3333333) / 13.3333333

def is_naidhana(lon):
    idx, frac = get_nakshatra_index(lon)
    return frac >= NAIDHANA_START_FRACTION

def get_scope_letter(nak_index):
    return SCOPE_LETTERS[nak_index % 4]

def main():
    dt_local, lat, lon = read_config()
    tz = get_timezone(lat, lon, dt_local)
    dt_utc = to_utc(dt_local, tz)
    jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60)
    swe.set_ephe_path(".")

    ayanamsa = get_ayanamsa(jd_ut)
    planets = get_planet_longitudes(jd_ut)
    asc = get_lagna(jd_ut, lat, lon)

    all_bodies = dict(planets)
    all_bodies["Lagna"] = asc

    symbols = []
    for p, lon in planets.items():
        sidereal_lon = (lon - ayanamsa) % 360
        house = get_house(sidereal_lon, asc)

        if is_naidhana(sidereal_lon):
            nak_idx, _ = get_nakshatra_index(sidereal_lon)
            scope_letter = get_scope_letter(nak_idx)
            symbols.append(f"N: {p[:2]}{house}({scope_letter}). ")

    print(" ".join(symbols))  # Output for Cinnamon panel

if __name__ == "__main__":
    main()
