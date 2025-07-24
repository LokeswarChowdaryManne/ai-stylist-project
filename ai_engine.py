from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import pickle

class AIEngine:
    def __init__(self, wardrobe_data, user_id):
        # 1. Load a pre-trained model when the engine is created.
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.wardrobe = wardrobe_data
        
        # Define a unique cache file for each user
        cache_filename = f"embeddings_user_{user_id}.pkl"
        
        # Check if a cached embeddings file exists
        if os.path.exists(cache_filename):
            print(f"Loading embeddings from cache for user {user_id}...")
            self.item_embeddings = self._load_embeddings(cache_filename)
        else:
            # If no cache exists, create embeddings and save them
            print(f"No cache found. Creating new embeddings for user {user_id}...")
            self.item_embeddings = self._create_and_save_embeddings(cache_filename)

    def _load_embeddings(self, filename):
        """Loads embeddings from a pickle file."""
        with open(filename, 'rb') as f:
            return pickle.load(f)

    def _create_and_save_embeddings(self, filename):
        """Creates embeddings and saves them to a pickle file."""
        descriptions = []
        for item in self.wardrobe:
            desc = (
                f"A {item['Style']} {item['Color']} {item['Pattern']} {item['Type']} "
                f"suitable for {item['ConditionType']} weather."
            )
            descriptions.append(desc)
        
        print("Creating AI embeddings for wardrobe...")
        embeddings = self.model.encode(descriptions)
        print("Embeddings created successfully.")
        
        # Save the newly created embeddings to the cache file
        with open(filename, 'wb') as f:
            pickle.dump(embeddings, f)
        print(f"Embeddings saved to {filename}.")
        return embeddings

    def score_outfit(self, shirt_idx, pants_idx, shoes_idx):
        """Calculates a compatibility score for an outfit using cosine similarity."""
        shirt_vec = self.item_embeddings[shirt_idx].reshape(1, -1)
        pants_vec = self.item_embeddings[pants_idx].reshape(1, -1)
        shoes_vec = self.item_embeddings[shoes_idx].reshape(1, -1)

        shirt_pants_sim = cosine_similarity(shirt_vec, pants_vec)[0][0]
        pants_shoes_sim = cosine_similarity(pants_vec, shoes_vec)[0][0]

        return (shirt_pants_sim + pants_shoes_sim) / 2