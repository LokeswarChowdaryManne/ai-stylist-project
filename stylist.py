import csv
import random

# Function to load the wardrobe from the CSV file
def load_wardrobe(filename="wardrobe.csv"):
    wardrobe = []
    with open(filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            wardrobe.append(row)
    return wardrobe

# Function to get suitable items based on context
def find_items(wardrobe, occasion, weather):
    suitable_shirts = []
    suitable_pants = []
    suitable_shoes = []
    suitable_tops = [] # For jackets, sweaters, etc.

    for item in wardrobe:
        # Basic rule: Style must match the occasion
        if item['Style'] == occasion:
            # Weather check
            is_weather_ok = (item['Weather'] == weather or item['Weather'] == 'All')

            if is_weather_ok:
                if item['Type'] == 'Shirt':
                    suitable_shirts.append(item)
                elif item['Type'] == 'Pants':
                    suitable_pants.append(item)
                elif item['Type'] == 'Shoes':
                    suitable_shoes.append(item)
                elif item['Type'] == 'Top' and weather == 'Cold': # Only suggest tops if it's cold
                    suitable_tops.append(item)
    
    return suitable_shirts, suitable_pants, suitable_shoes, suitable_tops

# --- Main Program ---
if __name__ == "__main__":
    # 1. Load the wardrobe data
    my_wardrobe = load_wardrobe()

    # 2. Get context from the user
    print("👔 Welcome to your Personal Stylist!")
    occasion_input = input("What is the occasion? (Formal/Casual): ").capitalize()
    weather_input = input("What is the weather? (Hot/Warm/Cold): ").capitalize()

    # 3. Find all possible items that match the context
    shirts, pants, shoes, tops = find_items(my_wardrobe, occasion_input, weather_input)

    # 4. Select a random outfit from the suitable items
    if shirts and pants and shoes:
        chosen_shirt = random.choice(shirts)
        chosen_pants = random.choice(pants)
        chosen_shoe = random.choice(shoes)
        chosen_top = None
        if tops:
            chosen_top = random.choice(tops)

        # 5. Display the suggestion
        print("\n✨ Here is your outfit suggestion:")
        print("---------------------------------")
        if chosen_top:
            print(f"Top:    {chosen_top['ItemName']} ({chosen_top['Color']})")
        print(f"Shirt:  {chosen_shirt['ItemName']} ({chosen_shirt['Color']})")
        print(f"Pants:  {chosen_pants['ItemName']} ({chosen_pants['Color']})")
        print(f"Shoes:  {chosen_shoe['ItemName']} ({chosen_shoe['Color']})")
        print("---------------------------------")
    else:
        print("\nSorry, I couldn't find a suitable outfit with your current wardrobe and criteria.")
        print("Try adding more items to wardrobe.csv or changing the occasion/weather.")