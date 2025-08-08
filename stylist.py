# stylist.py - Final version using custom trained model
import random

class Stylist:
    def __init__(self, wardrobe_data, ai_engine):
        self.wardrobe = wardrobe_data
        self.ai_engine = ai_engine
        # Generate embeddings for the entire current wardrobe ONCE
        self.wardrobe_embeddings = self._generate_all_embeddings()

    def _generate_all_embeddings(self):
        """Generates and stores embeddings for all items in the wardrobe."""
        print("Generating embeddings for user's wardrobe...")
        # We assume an ImagePath column exists in our data now
        image_paths = [item['ImagePath'] for item in self.wardrobe]
        embeddings = [self.ai_engine.get_embedding(path) for path in image_paths]
        return embeddings

    def get_suggestion(self, occasion, temperature, condition):
        # 1. Get all suitable items and their original indices
        suitable_items = {'shirts': [], 'pants': [], 'shoes': [], 'tops': []}
        original_indices = {'shirts': [], 'pants': [], 'shoes': []}

        for i, item in enumerate(self.wardrobe):
            is_condition_ok = (item['ConditionType'] == 'Any' or item['ConditionType'] == condition)
            if item['Style'].strip() == occasion and item['MinTemp'] <= temperature <= item['MaxTemp'] and is_condition_ok:
                item_type_map = {'shirt': 'shirts', 'pants': 'pants', 'shoes': 'shoes', 'top': 'tops'}
                item_type_key = item['Type'].lower()
                if item_type_key in item_type_map:
                    mapped_type = item_type_map[item_type_key]
                    suitable_items[mapped_type].append(item)
                    if mapped_type in original_indices:
                        original_indices[mapped_type].append(i)

        if not (suitable_items['shirts'] and suitable_items['pants'] and suitable_items['shoes']):
            return None

        # 2. Score all combinations using pre-computed embeddings
        best_outfit = None
        highest_score = -1

        for s_idx, shirt in enumerate(suitable_items['shirts']):
            for p_idx, pant in enumerate(suitable_items['pants']):
                for sh_idx, shoe in enumerate(suitable_items['shoes']):

                    # Get the embeddings using the original indices
                    shirt_vec = self.wardrobe_embeddings[original_indices['shirts'][s_idx]]
                    pants_vec = self.wardrobe_embeddings[original_indices['pants'][p_idx]]
                    shoes_vec = self.wardrobe_embeddings[original_indices['shoes'][sh_idx]]

                    # Calculate scores
                    shirt_pants_sim = cosine_similarity(shirt_vec, pants_vec)[0][0]
                    pants_shoes_sim = cosine_similarity(pants_vec, shoes_vec)[0][0]
                    score = (shirt_pants_sim + pants_shoes_sim) / 2

                    if score > highest_score:
                        highest_score = score
                        best_outfit = {'shirt': shirt, 'pants': pant, 'shoes': shoe}

        if best_outfit:
            best_outfit['top'] = random.choice(suitable_items['tops']) if suitable_items['tops'] else None
            return best_outfit

        return None