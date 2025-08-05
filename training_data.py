import os
import random
from PIL import Image
from tqdm import tqdm
import torch
from torch.utils.data import Dataset
from torchvision import transforms
import matplotlib.pyplot as plt

# --- 1. Configuration ---
# This section contains the main settings for our dataset preparation.
class Config:
    PROCESSED_DATA_DIR = "processed_images"
    # Assuming each outfit in the dataset consists of 3 items (e.g., top, bottom, shoes)
    ITEMS_PER_OUTFIT = 3 
    # Resize images to a consistent size for the model
    IMAGE_SIZE = (224, 224) 

# --- 2. The Custom PyTorch Dataset Class ---
class OutfitPairsDataset(Dataset):
    """
    A PyTorch Dataset class that serves pairs of images for training.
    It generates pairs on-the-fly:
    - 50% of the time, it returns a "positive pair" (two items from the same outfit).
    - 50% of the time, it returns a "negative pair" (two items from different outfits).
    """
    def __init__(self, root_dir, items_per_outfit, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.items_per_outfit = items_per_outfit
        
        # Get a sorted list of all image file paths
        self.image_files = sorted([os.path.join(root_dir, f) for f in os.listdir(root_dir) if f.endswith('.jpg')])
        self.num_images = len(self.image_files)
        self.num_outfits = self.num_images // self.items_per_outfit
        
        print(f"Found {self.num_images} images, creating {self.num_outfits} outfits.")

    def __len__(self):
        """Returns the total number of possible pairs we can generate."""
        # We can generate one pair for each image in the dataset.
        return self.num_images

    def __getitem__(self, index):
        """Gets a single item (a pair of images and a label) from the dataset."""
        
        # Decide whether to create a positive or negative pair
        should_get_positive_pair = random.random() < 0.5
        
        if should_get_positive_pair:
            # --- Create a POSITIVE pair (items from the same outfit) ---
            
            # 1. Figure out which outfit the given index belongs to.
            outfit_index = index // self.items_per_outfit
            
            # 2. Get the start and end index for all items in that outfit.
            start_index = outfit_index * self.items_per_outfit
            end_index = start_index + self.items_per_outfit
            
            # 3. Get all image paths for that outfit.
            outfit_image_paths = self.image_files[start_index:end_index]
            
            # 4. Randomly sample two different images from that outfit.
            anchor_path, pair_path = random.sample(outfit_image_paths, 2)
            
            label = 1.0 # 1.0 means "match"

        else:
            # --- Create a NEGATIVE pair (items from different outfits) ---

            # 1. Select the first image (the "anchor").
            anchor_path = self.image_files[index]
            
            # 2. Find the outfit of the anchor image.
            anchor_outfit_index = index // self.items_per_outfit
            
            # 3. Keep picking a random image until we find one from a DIFFERENT outfit.
            while True:
                random_index = random.randint(0, self.num_images - 1)
                random_outfit_index = random_index // self.items_per_outfit
                
                if random_outfit_index != anchor_outfit_index:
                    # Found an image from a different outfit. This is our negative pair.
                    pair_path = self.image_files[random_index]
                    break
            
            label = 0.0 # 0.0 means "mismatch"
        
        # Load the actual images from the file paths
        anchor_img = Image.open(anchor_path).convert("RGB")
        pair_img = Image.open(pair_path).convert("RGB")

        # Apply transformations (like resizing) if they were provided
        if self.transform:
            anchor_img = self.transform(anchor_img)
            pair_img = self.transform(pair_img)

        return anchor_img, pair_img, torch.tensor(label, dtype=torch.float32)

# --- 3. A Small Test to See it in Action ---
if __name__ == "__main__":
    # Define the transformations: Resize images and convert them to PyTorch tensors
    data_transforms = transforms.Compose([
        transforms.Resize(Config.IMAGE_SIZE),
        transforms.ToTensor()
    ])

    # Create an instance of our custom dataset
    outfit_dataset = OutfitPairsDataset(
        root_dir=Config.PROCESSED_DATA_DIR,
        items_per_outfit=Config.ITEMS_PER_OUTFIT,
        transform=data_transforms
    )

    # Let's get and display one sample from the dataset
    print("\nFetching one sample from the dataset...")
    anchor, pair, label = outfit_dataset[0] # Get the first sample

    print(f"Sample fetched. Label: {'Positive (match)' if label.item() == 1.0 else 'Negative (mismatch)'}")
    
    # Function to display the images
    def show_images(anchor_img, pair_img, title):
        fig, axs = plt.subplots(1, 2, figsize=(8, 4))
        # Convert tensor back to a format matplotlib can display
        axs[0].imshow(anchor_img.permute(1, 2, 0))
        axs[0].set_title("Anchor Image")
        axs[0].axis('off')

        axs[1].imshow(pair_img.permute(1, 2, 0))
        axs[1].set_title("Paired Image")
        axs[1].axis('off')

        fig.suptitle(title)
        plt.show()

    show_images(anchor, pair, f"Label: {'MATCH' if label.item() == 1.0 else 'MISMATCH'}")