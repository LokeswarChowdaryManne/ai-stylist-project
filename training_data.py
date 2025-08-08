import os
import random
from PIL import Image
from tqdm import tqdm
import torch
from torch.utils.data import Dataset
from torchvision import transforms
import matplotlib.pyplot as plt

# --- 1. Configuration ---
class Config:
    PROCESSED_DATA_DIR = "processed_images"
    ITEMS_PER_OUTFIT = 3 
    IMAGE_SIZE = (224, 224) 

# --- 2. The Custom PyTorch Dataset Class ---
class OutfitPairsDataset(Dataset):
    def __init__(self, root_dir, items_per_outfit, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.items_per_outfit = items_per_outfit
        
        self.image_files = sorted([os.path.join(root_dir, f) for f in os.listdir(root_dir) if f.endswith('.jpg')])
        self.num_images = len(self.image_files)
        self.num_outfits = self.num_images // self.items_per_outfit
        
        print(f"Found {self.num_images} images, creating {self.num_outfits} outfits.")

    def __len__(self):
        return self.num_images

    def __getitem__(self, index):
        should_get_positive_pair = random.random() < 0.5
        
        # Determine the outfit for the current index
        outfit_index = index // self.items_per_outfit
        start_index = outfit_index * self.items_per_outfit
        end_index = start_index + self.items_per_outfit
        outfit_image_paths = self.image_files[start_index:end_index]
        
        # THE FIX: Check if the outfit has enough images to form a positive pair.
        # If not, force the creation of a negative pair to prevent a crash.
        if len(outfit_image_paths) < 2:
            should_get_positive_pair = False

        if should_get_positive_pair:
            # --- Create a POSITIVE pair (items from the same outfit) ---
            anchor_path, pair_path = random.sample(outfit_image_paths, 2)
            label = 1.0
        else:
            # --- Create a NEGATIVE pair (items from different outfits) ---
            anchor_path = self.image_files[index]
            anchor_outfit_index = index // self.items_per_outfit
            
            while True:
                random_index = random.randint(0, self.num_images - 1)
                random_outfit_index = random_index // self.items_per_outfit
                
                if random_outfit_index != anchor_outfit_index:
                    pair_path = self.image_files[random_index]
                    break
            
            label = 0.0
        
        anchor_img = Image.open(anchor_path).convert("RGB")
        pair_img = Image.open(pair_path).convert("RGB")

        if self.transform:
            anchor_img = self.transform(anchor_img)
            pair_img = self.transform(pair_img)

        return anchor_img, pair_img, torch.tensor(label, dtype=torch.float32)
