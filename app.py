import requests
from flask import Flask, jsonify, request
from stylist import Stylist

app = Flask(__name__)
personal_stylist = Stylist()

# --- Weather API Configuration ---
WEATHER_API_KEY = "YOUR_API_KEY_HERE"  # <-- IMPORTANT: PASTE YOUR KEY HERE
COIMBATORE_LAT = 11.0168
COIMBATORE_LON = 76.9558
WEATHER_URL = f"https://api.openweathermap.org/data/2.5/weather?lat={COIMBATORE_LAT}&lon={COIMBATORE_LON}&appid={WEATHER_API_KEY}&units=metric"

def get_current_weather():
    """Fetches weather from OpenWeatherMap and returns temp and condition."""
    try:
        response = requests.get(WEATHER_URL, verify=False)
        response.raise_for_status()  # Raises an exception for bad responses (4xx or 5xx)
        data = response.json()
        temp = int(data['main']['temp'])
        # The main weather condition (e.g., 'Rain', 'Clouds', 'Clear')
        condition = data['weather'][0]['main']
        return temp, condition
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather: {e}")
        return None, None

@app.route("/suggest")
def get_outfit_suggestion():
    # Input is now only the occasion
    occasion = request.args.get('occasion', type=str)
    if not occasion:
        return jsonify({"error": "Missing required parameter: occasion"}), 400

    # Get weather automatically
    temp, condition = get_current_weather()
    if temp is None:
        return jsonify({"error": "Could not retrieve current weather data."}), 500
    
    outfit = personal_stylist.get_suggestion(occasion.capitalize(), temp, condition)

    if outfit:
        # Include current weather in the response
        outfit['current_weather'] = {'temperature': temp, 'condition': condition}
        return jsonify(outfit)
    else:
        return jsonify({"message": f"No suitable outfit found for {temp}°C and {condition} conditions."}), 404

@app.route("/")
def hello_world():
    return "<h1>Stylist Backend is running.</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)