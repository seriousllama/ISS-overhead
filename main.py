import os
import smtplib
from datetime import datetime, timezone
import requests

MY_LAT = float(os.environ["MY_LAT"])
MY_LONG = float(os.environ["MY_LONG"])
MY_EMAIL = os.environ["MY_EMAIL"]
APP_PASSWORD = os.environ["APP_PASSWORD"]

def iss_near():
    response = requests.get("http://api.open-notify.org/iss-now.json", timeout=10)
    response.raise_for_status()
    position = response.json()["iss_position"]
    iss_lat, iss_long = float(position["latitude"]), float(position["longitude"])
    near = abs(iss_lat - MY_LAT) <= 5 and abs(iss_long - MY_LONG) <= 5
    return near

def is_night():
    response = requests.get(
        "https://api.sunrise-sunset.org/json",
        params={"lat": MY_LAT, "lng": MY_LONG, "formatted": 0},
        timeout=10,
    )
    response.raise_for_status()
    results = response.json()["results"]
    sunrise = int(results["sunrise"].split("T")[1].split(":")[0])
    sunset = int(results["sunset"].split("T")[1].split(":")[0])
    now = datetime.now(timezone.utc).hour
    night = now >= sunset or now <= sunrise
    return night

if iss_near() and is_night():
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as connection:
        connection.starttls()
        connection.login(MY_EMAIL, APP_PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=MY_EMAIL,
            msg="Subject: The ISS is above\n\nLook up!",
        )