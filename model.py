# model.py
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models

class SiameseNetwork(nn.Module):
    """
    The Siamese Network architecture. It has one "tower" or "encoder" that
    processes each image.
    """
    def __init__(self, embedding_dim=128):
        super(SiameseNetwork, self).__init__()
        
        # 1. Load a pre-trained ResNet-18 model as the backbone
        self.backbone = models.resnet18(weights='IMAGENET1K_V1')
        
        # 2. Get the number of input features from the ResNet's final layer
        num_features = self.backbone.fc.in_features
        
        # 3. Replace the final classification layer with our custom "head"
        # The head will output our desired embedding vector.
        self.backbone.fc = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Linear(512, embedding_dim)
        )

    def forward_one(self, x):
        """Processes one image through the network."""
        return self.backbone(x)

    def forward(self, anchor, pair):
        """Processes a pair of images."""
        output1 = self.forward_one(anchor)
        output2 = self.forward_one(pair)
        return output1, output2

class ContrastiveLoss(nn.Module):
    """
    This is the special loss function that trains the Siamese Network.
    It pushes positive pairs closer together and negative pairs further apart.
    """
    def __init__(self, margin=2.0):
        super(ContrastiveLoss, self).__init__()
        self.margin = margin

    def forward(self, output1, output2, label):
        # Calculate the Euclidean distance between the two output vectors
        euclidean_distance = F.pairwise_distance(output1, output2, keepdim=True)
        
        # Calculate the loss
        loss_contrastive = torch.mean(
            (1 - label) * torch.pow(euclidean_distance, 2) +
            (label) * torch.pow(torch.clamp(self.margin - euclidean_distance, min=0.0), 2)
        )
        # The formula is slightly different from the standard one to match the label convention
        # (label=1 for positive/match, label=0 for negative/mismatch).
        # When label=1 (match), it tries to minimize the distance.
        # When label=0 (mismatch), it tries to make the distance at least as large as the margin.

        return loss_contrastive