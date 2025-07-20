import csv
import random

# --- RULE ENGINE ---
# Define basic color compatibility rules using ColorFamily.
# This is the "brain" of our stylist.
COLOR_RULES = {
    'Neutral': ['Neutral', 'Blue', 'Bold', 'Brown'],
    'Blue': ['Neutral', 'Brown'],
    'Brown': ['Neutral', 'Blue'],
    'Bold': ['Neutral'] # Bold colors (like red) pair best with neutrals.
}

def is_color_compatible(shirt, pants, shoes):
    """Checks if the color combination of an outfit is valid based on rules."""
    shirt_color = shirt['ColorFamily']
    pants_color = pants['ColorFamily']
    shoes_color = shoes['ColorFamily']

    # Rule 1: Pants color must be compatible with shirt color.
    if pants_color not in COLOR_RULES.get(shirt_color, []):
        return False
        
    # Rule 2: Shoes should match the pants or be neutral.
    # A classic rule: avoid black pants with brown shoes for formal wear.
    if pants_color == 'Neutral' and pants['Color'] == 'Black' and shoes_color == 'Brown':
        if shirt['Style'] == 'Formal': # This rule is stricter for formal wear
            return False

    # Rule 3: General shoe compatibility
    if shoes_color not in COLOR_RULES.get(pants_color, []):
        return False
        
    return True

# --- FILE HANDLING & ITEM SEARCH ---
def load_wardrobe(filename="wardrobe.csv"):
    """Loads wardrobe data from the specified CSV file."""
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            return list(csv.DictReader(file))
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
        return []

def find_items(wardrobe, occasion, weather):
    """Filters items from the wardrobe based on occasion and weather."""
    # Using dictionary comprehension for a cleaner look
    filters = {'Style': occasion}
    
    items = {
        'shirts': [item for item in wardrobe if item['Type'] == 'Shirt' and all(item[k] == v for k, v in filters.items()) and (item['Weather'] == weather or item['Weather'] == 'All')],
        'pants': [item for item in wardrobe if item['Type'] == 'Pants' and all(item[k] == v for k, v in filters.items()) and (item['Weather'] == weather or item['Weather'] == 'All')],
        'shoes': [item for item in wardrobe if item['Type'] == 'Shoes' and all(item[k] == v for k, v in filters.items()) and (item['Weather'] == weather or item['Weather'] == 'All')],
        'tops': [item for item in wardrobe if item['Type'] == 'Top' and all(item[k] == v for k, v in filters.items()) and weather == 'Cold']
    }
    return items

def find_outfit(items):
    """Tries to find a color-compatible outfit combination."""
    # Shuffle lists to get different results each time
    random.shuffle(items['shirts'])
    random.shuffle(items['pants'])
    random.shuffle(items['shoes'])

    # Iterate through possible combinations to find a match
    for shirt in items['shirts']:
        for pant in items['pants']:
            for shoe in items['shoes']:
                if is_color_compatible(shirt, pant, shoe):
                    # Found a good match!
                    top = random.choice(items['tops']) if items['tops'] else None
                    return shirt, pant, shoe, top
    
    # If no compatible combination is found after checking all
    return None, None, None, None

# --- MAIN PROGRAM ---
if __name__ == "__main__":
    my_wardrobe = load_wardrobe()
    if not my_wardrobe:
        exit() # Exit if wardrobe couldn't be loaded

    print("👔 Welcome to your Personal Stylist!")
    occasion_input = input("What is the occasion? (Formal/Casual): ").capitalize()
    weather_input = input("What is the weather? (Hot/Warm/Cold): ").capitalize()

    # Find all items that fit the basic criteria
    suitable_items = find_items(my_wardrobe, occasion_input, weather_input)

    # Find a complete, color-coordinated outfit
    chosen_shirt, chosen_pants, chosen_shoe, chosen_top = find_outfit(suitable_items)

    if chosen_shirt:
        print("\n✨ Here is your outfit suggestion:")
        print("---------------------------------")
        if chosen_top:
            print(f"Top:    {chosen_top['ItemName']} ({chosen_top['Color']})")
        print(f"Shirt:  {chosen_shirt['ItemName']} ({chosen_shirt['Color']})")
        print(f"Pants:  {chosen_pants['ItemName']} ({chosen_pants['Color']})")
        print(f"Shoes:  {chosen_shoe['ItemName']} ({chosen_shoe['Color']})")
        print("---------------------------------")
    else:
        print("\nSorry, I couldn't find a color-compatible outfit with your current wardrobe.")
        print("Try adding more items to wardrobe.csv or creating more flexible color rules.")