# auto_tagger.py
from sentence_transformers import SentenceTransformer, util
from PIL import Image

class AutoTagger:
    def __init__(self):
        print("Loading Vision-Language Model (CLIP)...")
        # Load a pre-trained multi-modal model
        self.model = SentenceTransformer('clip-ViT-B-32')
        print("VLM Model loaded.")

    def _predict_best_tag(self, image: Image.Image, tags: list[str]) -> str:
        """Finds the best matching tag for an image from a list of candidates."""
        # First, convert our text tags into numerical embeddings
        text_embeddings = self.model.encode(tags)

        # Then, convert the image into its own embedding
        image_embedding = self.model.encode(image)

        # Calculate the similarity between the image and each text tag
        similarities = util.cos_sim(image_embedding, text_embeddings)

        # Find the tag with the highest similarity score
        best_match_index = similarities.argmax()

        return tags[best_match_index]

    def tag_image(self, image: Image.Image):
        """Generates a full set of tags for a given clothing image."""
        print("Auto-tagging image...")

        # Define the possible options for each category
        type_options = ["Shirt", "Pants", "Shoes", "Jacket", "Tee", "Denim", "Sweater"]
        style_options = ["Formal", "Casual", "Sport"]
        color_options = ["Red", "Green", "Blue", "White", "Black", "Grey", "Brown", "Khaki", "Navy"]
        pattern_options = ["Solid", "Striped", "Checkered", "Graphic"]

        # Get the best tag for each category
        item_type = self._predict_best_tag(image, type_options)
        item_style = self._predict_best_tag(image, style_options)
        item_color = self._predict_best_tag(image, color_options)
        item_pattern = self._predict_best_tag(image, pattern_options)

        # For now, we'll keep some fields manual or with default values
        generated_tags = {
            "ItemName": f"{item_style} {item_color} {item_type}", # Auto-generate a name
            "Type": item_type,
            "Color": item_color,
            "ColorFamily": item_color, # Simple mapping for now
            "Style": item_style,
            "Pattern": item_pattern,
            "MinTemp": 15, # Default value
            "MaxTemp": 30, # Default value
            "ConditionType": "Any" # Default value
        }

        print(f"Generated Tags: {generated_tags}")
        return generated_tags