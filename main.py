import requests
import sys

# We use a dictionary to map Open-Meteo's WMO weather codes to readable text.
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}


def get_coordinates(city_name):
    """Fetches latitude and longitude for a given city name."""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&format=json"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "results" not in data:
            print(f"Error: Could not find location '{city_name}'. Please check the spelling.")
            sys.exit()

        location = data["results"][0]
        return {
            "name": location.get("name"),
            "country": location.get("country"),
            "latitude": location.get("latitude"),
            "longitude": location.get("longitude")
        }
    except requests.exceptions.RequestException as e:
        print(f"Network error while fetching location: {e}")
        sys.exit()


def get_weather(lat, lon):
    """Fetches current temperature, wind speed, and weather code."""
    # Notice we added 'weather_code' to the URL
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m,weather_code"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["current"]
    except requests.exceptions.RequestException as e:
        print(f"Network error while fetching weather: {e}")
        return None


def get_aqi(lat, lon):
    """Fetches current US Air Quality Index (AQI) and PM2.5."""
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi,pm2_5"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["current"]
    except requests.exceptions.RequestException as e:
        print(f"Network error while fetching AQI: {e}")
        return None


def main():
    print("=== Live Environment Fetcher ===")
    city_input = input("Enter a city name: ").strip()

    if not city_input:
        print("City name cannot be empty.")
        return

    print("\nFetching data...")

    # 1. Resolve Location
    location = get_coordinates(city_input)
    lat, lon = location["latitude"], location["longitude"]

    # 2. Fetch Data
    weather = get_weather(lat, lon)
    aqi_data = get_aqi(lat, lon)

    # 3. Display Results
    print("=" * 30)
    print(f"Location: {location['name']}, {location['country']}")
    print(f"Coordinates: {lat:.4f}, {lon:.4f}")
    print("-" * 30)

    if weather:
        # Get the code from the API, then look it up in our dictionary.
        # If the code isn't in the dictionary, it defaults to "Unknown condition".
        code = weather.get('weather_code')
        condition = WEATHER_CODES.get(code, "Unknown condition")

        print(f"Condition:   {condition}")
        print(f"Temperature: {weather['temperature_2m']} °C")
        print(f"Wind Speed:  {weather['wind_speed_10m']} km/h")
    else:
        print("Weather data currently unavailable.")

    if aqi_data:
        aqi_score = aqi_data.get('us_aqi')
        pm25 = aqi_data.get('pm2_5')
        print(f"US AQI:      {aqi_score}")
        print(f"PM 2.5:      {pm25} μg/m³")
    else:
        print("Air quality data currently unavailable.")
    print("=" * 30)


if __name__ == "__main__":
    main()