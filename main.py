# main.py
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# Import our new database functions and the simplified Stylist
from database import add_clothing_item, delete_clothing_item, get_wardrobe_by_user
from stylist import Stylist

# --- Pydantic Models (No changes here) ---
class ClothingItem(BaseModel):
    ItemName: str
    Type: str
    Color: str
    Style: str

class Weather(BaseModel):
    temperature: int
    condition: str

class OutfitResponse(BaseModel):
    top: Optional[ClothingItem] = None
    shirt: ClothingItem
    pants: ClothingItem
    shoes: ClothingItem
    current_weather: Weather

# Add this class to define the incoming data for a new clothing item
class NewClothingItem(BaseModel):
    ItemName: str
    Type: str
    Color: str
    ColorFamily: str
    Style: str
    Pattern: str
    MinTemp: int
    MaxTemp: int
    ConditionType: str

# Add this class for a simple confirmation message
class StatusResponse(BaseModel):
    status: str
    detail: str

# --- FastAPI App Setup ---
app = FastAPI()

# --- Weather API Configuration (No changes here) ---
WEATHER_API_KEY = "ac058b95d5d3473d9d0ecc0dac09c9ba"
COIMBATORE_LAT = 11.0168
COIMBATORE_LON = 76.9558
WEATHER_URL = f"https://api.openweathermap.org/data/2.5/weather?lat={COIMBATORE_LAT}&lon={COIMBATORE_LON}&appid={WEATHER_API_KEY}&units=metric"

def get_current_weather():
    try:
        response = requests.get(WEATHER_URL, verify=False)
        response.raise_for_status()
        data = response.json()
        return {"temperature": int(data['main']['temp']), "condition": data['weather'][0]['main']}
    except requests.exceptions.RequestException:
        return None

# --- API Endpoints ---
@app.get("/suggest/{user_id}", response_model=OutfitResponse)
def suggest_for_user(user_id: int, occasion: str):
    # 1. Fetch the user's wardrobe from the database
    wardrobe = get_wardrobe_by_user(user_id)
    if not wardrobe:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found or has an empty wardrobe.")

    # 2. Create a Stylist instance with that user's specific wardrobe
    personal_stylist = Stylist(wardrobe_data=wardrobe)

    # 3. Get weather and suggestion (same as before)
    weather = get_current_weather()
    if not weather:
        raise HTTPException(status_code=500, detail="Could not retrieve weather data.")

    outfit_data = personal_stylist.get_suggestion(occasion.capitalize(), weather['temperature'], weather['condition'])

    if outfit_data:
        response_data = {**outfit_data, "current_weather": weather}
        return response_data
    else:
        raise HTTPException(status_code=404, detail="No suitable outfit found.")

@app.post("/wardrobe/{user_id}", response_model=StatusResponse)
def add_to_wardrobe(user_id: int, item: NewClothingItem):
    # FastAPI uses the 'item: NewClothingItem' type hint to:
    # 1. Expect this data in the request body.
    # 2. Validate the incoming JSON against your Pydantic model.
    # 3. Convert the JSON into a Python object you can use.

    # Pydantic models can be converted to dicts
    success, detail = add_clothing_item(user_id, item.dict())

    if not success:
        raise HTTPException(status_code=400, detail=detail)

    return {"status": "success", "detail": detail}

@app.delete("/wardrobe/{user_id}/{item_id}", response_model=StatusResponse)
def delete_from_wardrobe(user_id: int, item_id: int):
    # The user_id and item_id are both path parameters.
    success, detail = delete_clothing_item(user_id, item_id)

    if not success:
        # If the item wasn't found, we return a 404 error.
        raise HTTPException(status_code=404, detail=detail)

    return {"status": "success", "detail": detail}

@app.get("/")
def read_root():
    return {"message": "Stylist Backend is running. Go to /docs for API documentation."}