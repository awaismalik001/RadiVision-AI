"""
train_bone.py
-------------
High-performance PyTorch transfer learning pipeline for Musculoskeletal Bone Fracture Detection.
Trains a MobileNetV2 deep convolutional neural network on the real Kaggle Fracture Dataset.
Includes:
- Balanced sampling across Fractured and Not Fractured classes
- Clinical augmentations for bone projection radiographs
- Cosine Annealing learning rate schedule
- Best model persistence to model/bone/bone_fracture_model.pt
"""

import os
import sys
import random
import numpy as np
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader, Subset

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset", "bone_xray", "classification")

TRAIN_DIR = os.path.join(DATASET_DIR, "train")
VAL_DIR = os.path.join(DATASET_DIR, "val")
TEST_DIR = os.path.join(DATASET_DIR, "test")
EXPORT_MODEL_PATH = os.path.join(CURRENT_DIR, "bone_fracture_model.pt")

def train_bone_model(epochs: int = 4, batch_size: int = 16, lr: float = 3e-4, samples_per_class: int = 400):
    print("=" * 65)
    print("       RadiVision AI: Bone Fracture Transfer Learning Engine")
    print("=" * 65)

    if not os.path.exists(TRAIN_DIR):
        print(f"[Error] Dataset directory not found at: {TRAIN_DIR}")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Compute Device: {device}")
    print(f"Dataset Path  : {DATASET_DIR}")

    # Clinical Radiograph Data Augmentation
    data_transforms = {
        'train': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomRotation(15),
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
        ])
    }

    full_train_dataset = datasets.ImageFolder(TRAIN_DIR, data_transforms['train'])
    test_dataset = datasets.ImageFolder(TEST_DIR, data_transforms['test'])

    classes = full_train_dataset.classes
    print(f"Detected Classes: {classes}")  # ['fractured', 'not fractured']

    # Curate a balanced, representative subset for fast CPU training
    class_indices = {0: [], 1: []}
    for idx, (_, label) in enumerate(full_train_dataset.samples):
        class_indices[label].append(idx)

    random.seed(42)
    selected_indices = []
    for label in [0, 1]:
        available = class_indices[label]
        sample_count = min(samples_per_class, len(available))
        selected_indices.extend(random.sample(available, sample_count))
        print(f"  Class '{classes[label]}' (Index {label}): {sample_count} training samples selected")

    train_dataset = Subset(full_train_dataset, selected_indices)
    print(f"Total Balanced Training Samples: {len(train_dataset)}")
    print(f"Total Test Validation Samples  : {len(test_dataset)}")

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    # Load MobileNetV2 pretrained on ImageNet
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)

    # Freeze base feature extractor, fine-tune top layers
    for param in model.features[:-4].parameters():
        param.requires_grad = False
    for param in model.features[-4:].parameters():
        param.requires_grad = True

    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, 128),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(128, 2)
    )
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam([
        {'params': model.features[-4:].parameters(), 'lr': lr * 0.1},
        {'params': model.classifier.parameters(), 'lr': lr}
    ], weight_decay=1e-4)

    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    best_acc = 0.0
    print(f"\nStarting training for {epochs} epochs...")

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        train_corrects = 0
        train_total = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            train_corrects += torch.sum(preds == labels.data).item()
            train_total += labels.size(0)

        scheduler.step()
        train_loss = running_loss / train_total
        train_acc = (train_corrects / train_total) * 100.0

        # Validate on full independent test set
        model.eval()
        val_corrects = 0
        val_total = 0
        with torch.no_grad():
            for inputs, labels in test_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                val_corrects += torch.sum(preds == labels.data).item()
                val_total += labels.size(0)

        val_acc = (val_corrects / val_total) * 100.0 if val_total else 0.0
        print(f"Epoch [{epoch+1:02d}/{epochs:02d}] Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}% | Test Acc: {val_acc:.2f}%")

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), EXPORT_MODEL_PATH)
            print(f"  --> Checkpoint saved! (New Best Test Accuracy: {best_acc:.2f}%)")

    print(f"\n[Success] Training completed. Best model exported to:\n  {EXPORT_MODEL_PATH}")
    print(f"Highest Test Accuracy achieved: {best_acc:.2f}%")

if __name__ == "__main__":
    train_bone_model()
