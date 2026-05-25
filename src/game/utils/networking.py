"""
This utility module is responsible for the networking requests, using
open-meteo.com's free APIs it gathers information on soil moisture and
soil temperature to be returned via its main function get_soil_conditions()
"""

import openmeteo_requests
import requests_cache
from retry_requests import retry

# Meteo is a free api.
# This module is just an  altered version from the following preset link
# I mean the python sample code option
# (split into multiple lines):
# https://open-meteo.com/en/docs?hourly=soil_moisture_9_to_27cm,
# soil_temperature_6cm&latitude=59.3294&longitude=18.0687&timezone=Europe%2FBerlin
# &wind_speed_unit=ms
cache = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache, retries=5, backoff_factor=0.2)
client = openmeteo_requests.Client(session=retry_session)

def get_soil_conditions():
    """
    Fetches current soil conditions for Stockholm using the Open-Meteo API.

    This function connects to the Open-Meteo weather API and retrieves
    hourly data for soil temperature and soil moisture. It extracts the
    most recent available values and returns them as integers for use
    in a simple game simulation.

    Returns:
        tuple: (soil_temperature_6cm, soil_moisture_9_to_27cm)
    """

    url = "https://api.open-meteo.com/v1/forecast"

    #Stockholm location. Europe/Berlin is same timezone as Stockholm (UTC-2 rigt now)
    params = {
        "latitude": 59.3294,
        "longitude": 18.0687,
        "hourly": [
            "soil_temperature_6cm",
            "soil_moisture_9_to_27cm"
        ],
        "timezone": "Europe/Berlin"
    }

    response = client.weather_api(url, params=params)[0]
    hourly = response.Hourly()

    soil_temp = hourly.Variables(0).ValuesAsNumpy()[0]
    soil_moisture = hourly.Variables(1).ValuesAsNumpy()[0]

    return float(soil_temp), float(soil_moisture)


if __name__ == "__main__":
    temp, moisture = get_soil_conditions()
    print(temp, moisture)
