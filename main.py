# main.py - Our FastAPI application
import requests
from fastapi import FastAPI, HTTPException
from stylist import Stylist # We still use our original Stylist class

# Create an instance of the FastAPI application
app = FastAPI()

# Create a single instance of the Stylist
personal_stylist = Stylist()

# --- Weather API Configuration ---
WEATHER_API_KEY = "ac058b95d5d3473d9d0ecc0dac09c9ba"  # <-- IMPORTANT: PASTE YOUR KEY HERE
COIMBATORE_LAT = 11.0168
COIMBATORE_LON = 76.9558
WEATHER_URL = f"https://api.openweathermap.org/data/2.5/weather?lat={COIMBATORE_LAT}&lon={COIMBATORE_LON}&appid={WEATHER_API_KEY}&units=metric"

def get_current_weather():
    """Fetches weather from OpenWeatherMap and returns temp and condition."""
    try:
        # The verify=False fix is still needed here
        response = requests.get(WEATHER_URL, verify=False)
        response.raise_for_status()
        data = response.json()
        temp = int(data['main']['temp'])
        condition = data['weather'][0]['main']
        return temp, condition
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather: {e}")
        return None, None

@app.get("/suggest")
def get_outfit_suggestion(occasion: str):
    # FastAPI handles missing parameters automatically.
    # We define 'occasion' as a required string parameter.

    temp, condition = get_current_weather()
    if temp is None:
        raise HTTPException(status_code=500, detail="Could not retrieve current weather data.")

    outfit = personal_stylist.get_suggestion(occasion.capitalize(), temp, condition)

    if outfit:
        outfit['current_weather'] = {'temperature': temp, 'condition': condition}
        return outfit
    else:
        raise HTTPException(status_code=404, detail=f"No suitable outfit found for {temp}°C and {condition} conditions.")

@app.get("/")
def read_root():
    return {"message": "Stylist Backend is running. Go to /docs for the API documentation."}