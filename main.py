import requests
import os # Import the 'os' module to interact with files
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from database import get_wardrobe_by_user, add_clothing_item, delete_clothing_item
from stylist import Stylist

# --- FastAPI App Setup ---
app = FastAPI()

# --- CORS Middleware Configuration ---
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models (No changes here) ---
class ClothingItem(BaseModel):
    ItemName: str
    Type: str
    Color: str
    Style: str

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

class Weather(BaseModel):
    temperature: int
    condition: str

class OutfitResponse(BaseModel):
    top: Optional[ClothingItem] = None
    shirt: ClothingItem
    pants: ClothingItem
    shoes: ClothingItem
    current_weather: Weather

class StatusResponse(BaseModel):
    status: str
    detail: str

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

# --- Helper function to delete cache ---
def clear_user_cache(user_id: int):
    cache_filename = f"embeddings_user_{user_id}.pkl"
    if os.path.exists(cache_filename):
        os.remove(cache_filename)
        print(f"Cache file {cache_filename} deleted.")

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Stylist Backend is running. Go to /docs for API documentation."}

@app.get("/suggest/{user_id}", response_model=OutfitResponse)
def suggest_for_user(user_id: int, occasion: str):
    weather = get_current_weather()
    if not weather:
        raise HTTPException(status_code=503, detail="Weather service is currently unavailable.")

    wardrobe = get_wardrobe_by_user(user_id)
    if not wardrobe:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found.")

    personal_stylist = Stylist(wardrobe_data=wardrobe, user_id=user_id)

    outfit_data = personal_stylist.get_suggestion(occasion.capitalize(), weather['temperature'], weather['condition'])

    if outfit_data:
        response_data = {**outfit_data, "current_weather": weather}
        return response_data
    else:
        raise HTTPException(status_code=404, detail="No suitable outfit found.")

@app.post("/wardrobe/{user_id}", response_model=StatusResponse)
def add_to_wardrobe(user_id: int, item: NewClothingItem):
    success, detail = add_clothing_item(user_id, item.dict())
    if not success:
        raise HTTPException(status_code=400, detail=detail)

    # Invalidate the cache after adding an item
    clear_user_cache(user_id)

    return {"status": "success", "detail": detail}

@app.delete("/wardrobe/{user_id}/{item_id}", response_model=StatusResponse)
def delete_from_wardrobe(user_id: int, item_id: int):
    success, detail = delete_clothing_item(user_id, item_id)
    if not success:
        raise HTTPException(status_code=404, detail=detail)

    # Invalidate the cache after deleting an item
    clear_user_cache(user_id)

    return {"status": "success", "detail": detail}