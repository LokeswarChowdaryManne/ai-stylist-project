# auto_tagger.py
from sentence_transformers import SentenceTransformer, util
from PIL import Image
from config import TAG_OPTIONS, DEFAULT_TAGS # Import from our new config file

class AutoTagger:
    def __init__(self):
        print("Loading Vision-Language Model (CLIP)...")
        self.model = SentenceTransformer('clip-ViT-B-32')
        print("VLM Model loaded.")

    def _predict_best_tag(self, image: Image.Image, tags: list[str]) -> str:
        """Finds the best matching tag for an image from a list of candidates."""
        text_embeddings = self.model.encode(tags)
        image_embedding = self.model.encode(image)
        similarities = util.cos_sim(image_embedding, text_embeddings)
        best_match_index = similarities.argmax()
        return tags[best_match_index]

    def tag_image(self, image: Image.Image):
        """Generates a full set of tags for a given clothing image."""
        print("Auto-tagging image...")

        # Get the best tag for each category by reading from the config
        item_type = self._predict_best_tag(image, TAG_OPTIONS["type"])
        item_style = self._predict_best_tag(image, TAG_OPTIONS["style"])
        item_color = self._predict_best_tag(image, TAG_OPTIONS["color"])
        item_pattern = self._predict_best_tag(image, TAG_OPTIONS["pattern"])

        # Combine the generated tags with the defaults from the config
        generated_tags = {
            "ItemName": f"{item_style} {item_color} {item_type}",
            "Type": item_type,
            "Color": item_color,
            "ColorFamily": item_color, # Simple mapping for now
            "Style": item_style,
            "Pattern": item_pattern,
            **DEFAULT_TAGS # Unpacks the default values (MinTemp, etc.)
        }

        print(f"Generated Tags: {generated_tags}")
        return generated_tags