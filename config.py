# config.py
# Central configuration for the AI Stylist application

# --- AI Auto-Tagger Settings ---
TAG_OPTIONS = {
    "type": ["Shirt", "Pants", "Shoes", "Jacket", "Tee", "Denim", "Sweater"],
    "style": ["Formal", "Casual", "Sport"],
    "color": ["Red", "Green", "Blue", "White", "Black", "Grey", "Brown", "Khaki", "Navy"],
    "pattern": ["Solid", "Striped", "Checkered", "Graphic"]
}

# --- Default values for new items ---
DEFAULT_TAGS = {
    "MinTemp": 15,
    "MaxTemp": 30,
    "ConditionType": "Any"
}