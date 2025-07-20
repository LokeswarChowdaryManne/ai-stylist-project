import csv
import random

class Stylist:
    COLOR_RULES = {
        'Neutral': ['Neutral', 'Blue', 'Bold', 'Brown'], 'Blue': ['Neutral', 'Brown', 'Blue'],
        'Brown': ['Neutral', 'Blue'], 'Bold': ['Neutral']
    }

    def __init__(self, wardrobe_file="wardrobe.csv"):
        self.wardrobe = self._load_wardrobe(wardrobe_file)

    def _load_wardrobe(self, filename):
        """Loads wardrobe data from the specified CSV file."""
        wardrobe_data = []
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Robust check for corrupted rows before processing
                    if row and row.get('Style') and row.get('MinTemp') and row.get('MaxTemp'):
                        row['MinTemp'] = int(row['MinTemp'].strip())
                        row['MaxTemp'] = int(row['MaxTemp'].strip())
                        wardrobe_data.append(row)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error loading wardrobe: {e}")
            return []
        return wardrobe_data

    def _is_color_compatible(self, shirt, pants, shoes):
        shirt_color, pants_color, shoes_color = shirt['ColorFamily'], pants['ColorFamily'], shoes['ColorFamily']
        if pants_color not in self.COLOR_RULES.get(shirt_color, []): return False
        if shirt['Style'] == 'Formal' and pants['Color'] == 'Black' and shoes_color == 'Brown': return False
        if shoes_color not in self.COLOR_RULES.get(pants_color, []): return False
        return True

    def get_suggestion(self, occasion, temperature):
        suitable_items = {'shirts': [], 'pants': [], 'shoes': [], 'tops': []}
        for item in self.wardrobe:
            if item['Style'].strip() == occasion and item['MinTemp'] <= temperature <= item['MaxTemp']:
                # Your corrected pluralization logic
                item_type_map = {
                    'shirt': 'shirts',
                    'pants': 'pants',
                    'shoes': 'shoes',
                    'top': 'tops'
                }
                item_type = item_type_map.get(item['Type'].lower())
                if item_type in suitable_items:
                    suitable_items[item_type].append(item)
        
        if not (suitable_items['shirts'] and suitable_items['pants'] and suitable_items['shoes']): return None
        
        random.shuffle(suitable_items['shirts'])
        random.shuffle(suitable_items['pants'])
        random.shuffle(suitable_items['shoes'])

        for shirt in suitable_items['shirts']:
            for pant in suitable_items['pants']:
                for shoe in suitable_items['shoes']:
                    if self._is_color_compatible(shirt, pant, shoe):
                        top = random.choice(suitable_items['tops']) if suitable_items['tops'] else None
                        return {'top': top, 'shirt': shirt, 'pants': pant, 'shoes': shoe}
        return None

# --- Main Program Execution ---
if __name__ == "__main__":
    personal_stylist = Stylist()
    if not personal_stylist.wardrobe: exit()

    print("👔 Welcome to your Personal Stylist!")
    occasion_input = input("What is the occasion? (Formal/Casual): ").strip().capitalize()
    
    try: temp_input = int(input("What is the current temperature (°C)?: "))
    except ValueError: print("Invalid temperature."); exit()

    outfit = personal_stylist.get_suggestion(occasion_input, temp_input)

    if outfit:
        print("\n✨ Here is your outfit suggestion:")
        print("---------------------------------")
        if outfit['top']: print(f"Top:    {outfit['top']['ItemName']} ({outfit['top']['Color']})")
        print(f"Shirt:  {outfit['shirt']['ItemName']} ({outfit['shirt']['Color']})")
        print(f"Pants:  {outfit['pants']['ItemName']} ({outfit['pants']['Color']})")
        print(f"Shoes:  {outfit['shoes']['ItemName']} ({outfit['shoes']['Color']})")
        print("---------------------------------")
    else:
        print("\nSorry, I couldn't find a suitable outfit for this temperature and occasion.")