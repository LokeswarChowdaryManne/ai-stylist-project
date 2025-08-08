# inference.py
import torch
from torchvision import transforms
from PIL import Image
import random
import os
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from model import SiameseNetwork # We import the same model structure

# --- Configuration ---
class InferenceConfig:
    PROCESSED_DATA_DIR = "processed_images"
    IMAGE_SIZE = (224, 224)
    MODEL_PATH = "stylist_model.pth"

# --- Main Inference Class ---
class InferenceEngine:
    def __init__(self):
        # Set up device, model, and transformations
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")

        self.model = SiameseNetwork()
        self.model.load_state_dict(torch.load(InferenceConfig.MODEL_PATH, map_location=self.device))
        self.model.to(self.device)
        self.model.eval() # IMPORTANT: Set model to evaluation mode

        self.transform = transforms.Compose([
            transforms.Resize(InferenceConfig.IMAGE_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def get_embedding(self, image_path):
        """Processes an image and returns its style embedding."""
        image = Image.open(image_path).convert("RGB")
        image_tensor = self.transform(image).unsqueeze(0) # Add batch dimension
        image_tensor = image_tensor.to(self.device)

        with torch.no_grad(): # Deactivate autograd for faster inference
            embedding = self.model.forward_one(image_tensor)

        return embedding.cpu().numpy()
