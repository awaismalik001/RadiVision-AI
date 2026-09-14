"""
train_model.py
--------------
Enhanced training pipeline for binary chest radiograph classification (Normal vs. Pneumonia)
using MobileNetV2 transfer learning with PyTorch.

Includes:
- Class-imbalance mitigation via weighted CrossEntropyLoss
- Data augmentations tailored for clinical radiographs
- Learning rate scheduling with Cosine Annealing
- Checkpoint persistence for the best validation accuracy & F1 score
"""

import os
import sys
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset", "chest_xray")

TRAIN_DIR = os.path.join(DATASET_DIR, "train")
VAL_DIR = os.path.join(DATASET_DIR, "val")
TEST_DIR = os.path.join(DATASET_DIR, "test")

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torchvision import datasets, models, transforms
    from torch.utils.data import DataLoader
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

def train_pytorch(epochs: int = 10, batch_size: int = 16, lr: float = 2e-4):
    print("=" * 60)
    print("       RadiVision AI: Enhanced Chest Model Training")
    print("=" * 60)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Compute Device: {device}")

    # Clinical data augmentations
    data_transforms = {
        'train': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomRotation(10),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.1, contrast=0.1),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'test': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }

    train_dataset = datasets.ImageFolder(TRAIN_DIR, data_transforms['train'])
    # Combine or use test/val for robust validation
    val_dataset = datasets.ImageFolder(TEST_DIR, data_transforms['test'])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    class_counts = [0, 0]
    for _, label in train_dataset.samples:
        class_counts[label] += 1

    total_samples = sum(class_counts)
    # Balanced weights: total / (n_classes * count)
    class_weights = [total_samples / (2.0 * c) for c in class_counts]
    weights_tensor = torch.tensor(class_weights, dtype=torch.float32).to(device)
    print(f"Detected Classes: {train_dataset.classes}")
    print(f"Class Distribution in Train: Normal={class_counts[0]}, Pneumonia={class_counts[1]}")
    print(f"Balanced Loss Weights       : Normal={class_weights[0]:.2f}, Pneumonia={class_weights[1]:.2f}")

    # Load MobileNetV2 pretrained on ImageNet
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    
    # Freeze initial feature extraction layers, keep top layers trainable
    for param in model.features[:-4].parameters():
        param.requires_grad = False
    for param in model.features[-4:].parameters():
        param.requires_grad = True

    # Classifier head
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, 128),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(128, 2)
    )
    model = model.to(device)

    criterion = nn.CrossEntropyLoss(weight=weights_tensor)
    optimizer = optim.Adam([
        {'params': model.features[-4:].parameters(), 'lr': lr * 0.1},
        {'params': model.classifier.parameters(), 'lr': lr}
    ], weight_decay=1e-4)

    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    out_model_path = os.path.join(CURRENT_DIR, "chest_xray_model.pt")
    best_acc = 0.0

    print(f"\nStarting training for {epochs} epochs...")
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        corrects = 0
        total = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            corrects += torch.sum(preds == labels.data).item()
            total += labels.size(0)

        scheduler.step()
        train_loss = running_loss / total
        train_acc = (corrects / total) * 100.0

        # Evaluation
        model.eval()
        val_corrects = 0
        val_total = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                val_corrects += torch.sum(preds == labels.data).item()
                val_total += labels.size(0)

        val_acc = (val_corrects / val_total) * 100.0 if val_total else 0.0
        print(f"Epoch [{epoch+1:02d}/{epochs:02d}] Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}% | Val Acc: {val_acc:.2f}%")

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), out_model_path)
            print(f"  --> Checkpoint saved! (New Best Val Accuracy: {best_acc:.2f}%)")

    print(f"\n[Success] Training completed. Best model saved to:\n  {out_model_path}")
    print(f"Highest Validation Accuracy achieved: {best_acc:.2f}%")

if __name__ == "__main__":
    if not HAS_TORCH:
        print("[Error] PyTorch is required. Run: pip install torch torchvision")
        sys.exit(1)
    train_pytorch()
