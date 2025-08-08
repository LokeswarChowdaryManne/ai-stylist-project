import os
import shutil
import time
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import requests
from rembg import remove
from PIL import Image

# --- Custom Module Imports ---
from auto_tagger import AutoTagger
from database import get_wardrobe_by_user, add_clothing_item, delete_clothing_item
from stylist import Stylist
from ai_engine import InferenceEngine

# Load environment variables from .env file
load_dotenv()

# --- App and AI Engine Setup ---
app = FastAPI()
ai_engine = InferenceEngine()
auto_tagger = AutoTagger()

# --- CORS Middleware Configuration ---
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class ClothingItem(BaseModel): ItemName: str; Type: str; Color: str; Style: str
class NewClothingItem(BaseModel): ItemName: str; Type: str; Color: str; ColorFamily: str; Style: str; Pattern: str; MinTemp: int; MaxTemp: int; ConditionType: str
class Weather(BaseModel): temperature: int; condition: str
class OutfitResponse(BaseModel): top: Optional[ClothingItem] = None; shirt: ClothingItem; pants: ClothingItem; shoes: ClothingItem; current_weather: Weather
class StatusResponse(BaseModel): status: str; detail: str
class AutoTagResponse(BaseModel): tags: NewClothingItem

# --- Weather API Configuration ---
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
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

def clear_user_cache(user_id: int):
    cache_filename = f"embeddings_user_{user_id}.pkl"
    if os.path.exists(cache_filename):
        os.remove(cache_filename)
        print(f"Cache file {cache_filename} deleted.")

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Stylist Backend is running. Go to /docs."}

@app.post("/wardrobe/{user_id}/upload-and-tag", response_model=AutoTagResponse)
def analyze_and_tag_image(user_id: int, file: UploadFile = File(...)):
    try:
        input_image = Image.open(file.file)
        clean_image = remove(input_image)
        tags = auto_tagger.tag_image(clean_image)
        return {"tags": tags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze image: {e}")

@app.post("/wardrobe/{user_id}/add-verified", response_model=StatusResponse)
def add_verified_item(user_id: int, file: UploadFile = File(...), item_data: str = Form(...)):
    try:
        item_dict = json.loads(item_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid item data format.")

    final_filename = f"{item_dict['ItemName'].replace(' ', '_')}_{user_id}_{int(time.time())}.png"
    final_file_path = os.path.join("uploads", final_filename)
    
    try:
        input_image = Image.open(file.file)
        output_image = remove(input_image)
        output_image.save(final_file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process and save image: {e}")
    
    success, detail = add_clothing_item(user_id, item_dict, final_file_path)
    
    if not success:
        raise HTTPException(status_code=400, detail=detail)
    
    clear_user_cache(user_id)
    return {"status": "success", "detail": f"Item '{item_dict['ItemName']}' added successfully."}

@app.get("/suggest/{user_id}", response_model=OutfitResponse)
def suggest_for_user(user_id: int, occasion: str):
    weather = get_current_weather()
    if not weather:
        raise HTTPException(status_code=503, detail="Weather service unavailable.")

    wardrobe = get_wardrobe_by_user(user_id)
    if not wardrobe:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found.")
    
    wardrobe_with_images = [item for item in wardrobe if item.get('ImagePath') and os.path.exists(item['ImagePath'])]
    if not wardrobe_with_images:
        raise HTTPException(status_code=404, detail="User wardrobe has no items with valid images.")
        
    personal_stylist = Stylist(wardrobe_data=wardrobe_with_images, ai_engine=ai_engine)
    
    outfit_data = personal_stylist.get_suggestion(occasion.capitalize(), weather['temperature'], weather['condition'])

    if outfit_data:
        response_data = {**outfit_data, "current_weather": weather}
        return response_data
    else:
        raise HTTPException(status_code=404, detail="No suitable outfit found.")
        
@app.delete("/wardrobe/{user_id}/{item_id}", response_model=StatusResponse)
def delete_from_wardrobe(user_id: int, item_id: int):
    success, detail = delete_clothing_item(user_id, item_id)
    if not success:
        raise HTTPException(status_code=404, detail=detail)
    clear_user_cache(user_id)
    return {"status": "success", "detail": detail}
