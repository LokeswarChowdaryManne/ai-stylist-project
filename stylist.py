import csv
import random

class Stylist:
    """
    An OOP-based stylist that suggests outfits from a wardrobe
    based on occasion, temperature, and color coordination rules.
    """
    
    # Class attribute for color rules
    COLOR_RULES = {
        'Neutral': ['Neutral', 'Blue', 'Bold', 'Brown'],
        'Blue': ['Neutral', 'Brown'],
        'Brown': ['Neutral', 'Blue'],
        'Bold': ['Neutral']
    }

    def __init__(self, wardrobe_file="wardrobe.csv"):
        self.wardrobe = self._load_wardrobe(wardrobe_file)

    def _load_wardrobe(self, filename):
        """Loads wardrobe data from the specified CSV file."""
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                # Convert temperature strings to integers during loading
                wardrobe_data = []
                for row in csv.DictReader(file):
                    row['MinTemp'] = int(row['MinTemp'])
                    row['MaxTemp'] = int(row['MaxTemp'])
                    wardrobe_data.append(row)
                return wardrobe_data
        except FileNotFoundError:
            print(f"Error: The file {filename} was not found.")
            return []
        except ValueError:
            print(f"Error: Could not convert temperature to a number in {filename}. Check your data.")
            return []

    def _is_color_compatible(self, shirt, pants, shoes):
        """Checks if the color combination of an outfit is valid."""
        shirt_color = shirt['ColorFamily']
        pants_color = pants['ColorFamily']
        shoes_color = shoes['ColorFamily']

        if pants_color not in self.COLOR_RULES.get(shirt_color, []):
            return False
        
        if shirt['Style'] == 'Formal' and pants['Color'] == 'Black' and shoes_color == 'Brown':
            return False

        if shoes_color not in self.COLOR_RULES.get(pants_color, []):
            return False
            
        return True

    def get_suggestion(self, occasion, temperature):
        """Finds and returns a color-compatible outfit suggestion."""
        # 1. Filter items by occasion and temperature
        suitable_items = {
            'shirts': [], 'pants': [], 'shoes': [], 'tops': []
        }
        for item in self.wardrobe:
            if item['Style'] == occasion and item['MinTemp'] <= temperature <= item['MaxTemp']:
                item_type = item['Type'].lower() + 's' # e.g., 'Shirt' -> 'shirts'
                if item_type in suitable_items:
                    suitable_items[item_type].append(item)
        
        # 2. Find a compatible combination
        random.shuffle(suitable_items['shirts'])
        random.shuffle(suitable_items['pants'])
        random.shuffle(suitable_items['shoes'])

        for shirt in suitable_items['shirts']:
            for pant in suitable_items['pants']:
                for shoe in suitable_items['shoes']:
                    if self._is_color_compatible(shirt, pant, shoe):
                        # Found a good match!
                        top = random.choice(suitable_items['tops']) if suitable_items['tops'] else None
                        return {'top': top, 'shirt': shirt, 'pants': pant, 'shoes': shoe}
        
        return None # No suitable outfit found

# --- Main Program Execution ---
if __name__ == "__main__":
    # Create an instance of the Stylist
    personal_stylist = Stylist()

    if not personal_stylist.wardrobe:
        exit() # Exit if wardrobe is empty or failed to load

    print("👔 Welcome to your Personal Stylist!")
    occasion_input = input("What is the occasion? (Formal/Casual): ").capitalize()
    
    try:
        temp_input = int(input("What is the current temperature (°C)?: "))
    except ValueError:
        print("Invalid temperature. Please enter a number.")
        exit()

    # Get a suggestion from our stylist instance
    outfit = personal_stylist.get_suggestion(occasion_input, temp_input)

    if outfit:
        print("\n✨ Here is your outfit suggestion:")
        print("---------------------------------")
        if outfit['top']:
            print(f"Top:    {outfit['top']['ItemName']} ({outfit['top']['Color']})")
        print(f"Shirt:  {outfit['shirt']['ItemName']} ({outfit['shirt']['Color']})")
        print(f"Pants:  {outfit['pants']['ItemName']} ({outfit['pants']['Color']})")
        print(f"Shoes:  {outfit['shoes']['ItemName']} ({outfit['shoes']['Color']})")
        print("---------------------------------")
    else:
        print("\nSorry, I couldn't find a suitable outfit for this temperature and occasion.")