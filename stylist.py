import random
from ai_engine import AIEngine

class Stylist:
    def __init__(self, wardrobe_data, user_id):
        self.wardrobe = wardrobe_data
        # Pass user_id to the AIEngine to handle caching
        self.ai_engine = AIEngine(self.wardrobe, user_id)

    def get_suggestion(self, occasion, temperature, condition):
        # 1. Get all suitable items based on context
        suitable_items = {'shirts': [], 'pants': [], 'shoes': [], 'tops': []}
        item_indices = {'shirts': [], 'pants': [], 'shoes': []} # To keep track of original index

        for i, item in enumerate(self.wardrobe):
            is_condition_ok = (item['ConditionType'] == 'Any' or item['ConditionType'] == condition)
            
            if item['Style'].strip() == occasion and item['MinTemp'] <= temperature <= item['MaxTemp'] and is_condition_ok:
                item_type_map = {'shirt': 'shirts', 'pants': 'pants', 'shoes': 'shoes', 'top': 'tops'}
                item_type_key = item['Type'].lower()

                if item_type_key in item_type_map:
                    mapped_type = item_type_map[item_type_key]
                    suitable_items[mapped_type].append(item)
                    if mapped_type in item_indices:
                        item_indices[mapped_type].append(i) # Save the original index
        
        if not (suitable_items['shirts'] and suitable_items['pants'] and suitable_items['shoes']):
            return None

        # 2. Score all possible combinations and find the best one
        best_outfit = None
        highest_score = -1 

        for s_idx, shirt in enumerate(suitable_items['shirts']):
            for p_idx, pant in enumerate(suitable_items['pants']):
                for sh_idx, shoe in enumerate(suitable_items['shoes']):
                    
                    original_s_idx = item_indices['shirts'][s_idx]
                    original_p_idx = item_indices['pants'][p_idx]
                    original_sh_idx = item_indices['shoes'][sh_idx]
                    
                    score = self.ai_engine.score_outfit(original_s_idx, original_p_idx, original_sh_idx)

                    if score > highest_score:
                        highest_score = score
                        best_outfit = {'shirt': shirt, 'pants': pant, 'shoes': shoe}

        if best_outfit:
            best_outfit['top'] = random.choice(suitable_items['tops']) if suitable_items['tops'] else None
            return best_outfit

        return None