# ai_engine.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class AIEngine:
    def __init__(self, wardrobe_data):
        # 1. Load a pre-trained model when the engine is created.
        # 'all-MiniLM-L6-v2' is a small but powerful model.
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # 2. Pre-process the wardrobe data and create embeddings.
        self.wardrobe = wardrobe_data
        self.item_embeddings = self._create_embeddings()

    def _create_embeddings(self):
        """Converts each clothing item into a text description and then into an embedding."""
        descriptions = []
        for item in self.wardrobe:
            # Create a descriptive sentence for each item.
            desc = (
                f"A {item['Style']} {item['Color']} {item['Pattern']} {item['Type']} "
                f"suitable for {item['ConditionType']} weather."
            )
            descriptions.append(desc)

        print("Creating AI embeddings for wardrobe...")
        # The model converts the list of sentences into a list of vectors (embeddings).
        embeddings = self.model.encode(descriptions)
        print("Embeddings created successfully.")
        return embeddings

    def score_outfit(self, shirt_idx, pants_idx, shoes_idx):
        """Calculates a compatibility score for an outfit using cosine similarity."""
        # Get the pre-computed embeddings for the items
        shirt_vec = self.item_embeddings[shirt_idx]
        pants_vec = self.item_embeddings[pants_idx]
        shoes_vec = self.item_embeddings[shoes_idx]

        # Reshape vectors for the cosine_similarity function
        shirt_vec = shirt_vec.reshape(1, -1)
        pants_vec = pants_vec.reshape(1, -1)
        shoes_vec = shoes_vec.reshape(1, -1)

        # Calculate similarity between pairs
        shirt_pants_sim = cosine_similarity(shirt_vec, pants_vec)[0][0]
        pants_shoes_sim = cosine_similarity(pants_vec, shoes_vec)[0][0]

        # Return the average similarity as the outfit's score
        return (shirt_pants_sim + pants_shoes_sim) / 2