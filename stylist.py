import random

class Stylist:
    COLOR_RULES = {
        'Neutral': ['Neutral', 'Blue', 'Bold', 'Brown'], 'Blue': ['Neutral', 'Brown', 'Blue'],
        'Brown': ['Neutral', 'Blue'], 'Bold': ['Neutral']
    }

    def __init__(self, wardrobe_data):
        # The wardrobe is now passed in during creation
        self.wardrobe = wardrobe_data

    # ... The rest of the methods (_is_color_compatible, get_suggestion) remain exactly the same ...
    # Make sure to rename the 'Condition' key to 'ConditionType' in get_suggestion
    def get_suggestion(self, occasion, temperature, condition):
        suitable_items = {'shirts': [], 'pants': [], 'shoes': [], 'tops': []}
        for item in self.wardrobe:
            is_condition_ok = (item['ConditionType'] == 'Any' or item['ConditionType'] == condition)

            if item['Style'].strip() == occasion and item['MinTemp'] <= temperature <= item['MaxTemp'] and is_condition_ok:
                item_type_map = { 'shirt': 'shirts', 'pants': 'pants', 'shoes': 'shoes', 'top': 'tops' }
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

    def _is_color_compatible(self, shirt, pants, shoes):
        shirt_color, pants_color, shoes_color = shirt['ColorFamily'], pants['ColorFamily'], shoes['ColorFamily']
        if pants_color not in self.COLOR_RULES.get(shirt_color, []): return False
        if shirt['Style'] == 'Formal' and pants['Color'] == 'Black' and shoes_color == 'Brown': return False
        if shoes_color not in self.COLOR_RULES.get(pants_color, []): return False
        return True

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