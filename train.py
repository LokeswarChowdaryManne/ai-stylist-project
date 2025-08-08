import torch
from torch.utils.data import DataLoader
from torchvision import transforms
import torch.optim as optim

from model import SiameseNetwork, ContrastiveLoss
from training_data import OutfitPairsDataset

# --- 1. Configuration ---
class TrainConfig:
    PROCESSED_DATA_DIR = "processed_images"
    ITEMS_PER_OUTFIT = 3
    IMAGE_SIZE = (224, 224)
    
    # Training Parameters
    BATCH_SIZE = 32
    NUM_EPOCHS = 10
    LEARNING_RATE = 0.0005
    MODEL_SAVE_PATH = "stylist_model.pth"

# --- 2. The Main Training Function ---
def train():
    """
    Main function to run the training process.
    """
    print("Starting the training process...")

    # Set the device to GPU if available, otherwise CPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Define data transformations
    data_transforms = transforms.Compose([
        transforms.Resize(TrainConfig.IMAGE_SIZE),
        transforms.ToTensor(),
        # Normalize with standard values for models pre-trained on ImageNet
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # Create the dataset
    print("Loading dataset...")
    dataset = OutfitPairsDataset(
        root_dir=TrainConfig.PROCESSED_DATA_DIR,
        items_per_outfit=TrainConfig.ITEMS_PER_OUTFIT,
        transform=data_transforms
    )

    # Create the DataLoader
    # DataLoader handles shuffling, batching, and loading data in parallel.
    train_loader = DataLoader(
        dataset,
        batch_size=TrainConfig.BATCH_SIZE,
        shuffle=True,
        num_workers=4 # Use 4 parallel processes to load data
    )

    # Initialize the model, loss function, and optimizer
    model = SiameseNetwork().to(device)
    criterion = ContrastiveLoss()
    optimizer = optim.Adam(model.parameters(), lr=TrainConfig.LEARNING_RATE)

    print("Starting training loop...")
    # --- The Training Loop ---
    for epoch in range(TrainConfig.NUM_EPOCHS):
        running_loss = 0.0
        
        # Iterate over batches of data from the DataLoader
        for i, (anchor, pair, label) in enumerate(train_loader):
            # Move the data to the selected device (GPU or CPU)
            anchor, pair, label = anchor.to(device), pair.to(device), label.to(device)
            
            # Zero the parameter gradients (important for every batch)
            optimizer.zero_grad()
            
            # Forward pass: compute predicted outputs by passing inputs to the model
            output1, output2 = model(anchor, pair)
            
            # Calculate the batch loss
            loss = criterion(output1, output2, label)
            
            # Backward pass: compute gradient of the loss with respect to model parameters
            loss.backward()
            
            # Perform a single optimization step (parameter update)
            optimizer.step()
            
            # Print statistics
            running_loss += loss.item()
            if i % 100 == 99: # Print every 100 mini-batches
                print(f"Epoch [{epoch+1}/{TrainConfig.NUM_EPOCHS}], Step [{i+1}/{len(train_loader)}], Loss: {running_loss / 100:.4f}")
                running_loss = 0.0

    print("Finished Training.")
    
    # Save the trained model
    print(f"Saving model to {TrainConfig.MODEL_SAVE_PATH}")
    torch.save(model.state_dict(), TrainConfig.MODEL_SAVE_PATH)
    print("Model saved successfully.")

# --- 3. Run the training ---
if __name__ == '__main__':
    # This check is important for multiprocessing on Windows
    train()