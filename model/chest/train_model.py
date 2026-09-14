"""
train_model.py
--------------
Trains a binary chest X-ray classifier (Normal vs. Pneumonia) using transfer 
learning with MobileNetV2. 
Supports both PyTorch (recommended for Python 3.12-3.14 on Windows) and TensorFlow/Keras.

Directory Structure Expected:
    dataset/chest_xray/
        train/
            NORMAL/
            PNEUMONIA/
        val/
            NORMAL/
            PNEUMONIA/
        test/
            NORMAL/
            PNEUMONIA/
"""

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset", "chest_xray")

TRAIN_DIR = os.path.join(DATASET_DIR, "train")
VAL_DIR = os.path.join(DATASET_DIR, "val")
TEST_DIR = os.path.join(DATASET_DIR, "test")

# Prefer PyTorch if available (works on Python 3.10 through 3.14)
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torchvision import datasets, models, transforms
    from torch.utils.data import DataLoader
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    import tensorflow as tf
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
    from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
    from tensorflow.keras.models import Model
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    HAS_TF = True
except ImportError:
    HAS_TF = False

def train_pytorch():
    print("[AI Training] Running PyTorch MobileNetV2 pipeline...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"  Using compute device: {device}")

    # Data augmentations & normalization
    data_transforms = {
        'train': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomRotation(15),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }

    train_dataset = datasets.ImageFolder(TRAIN_DIR, data_transforms['train'])
    val_dataset = datasets.ImageFolder(VAL_DIR, data_transforms['val'])

    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)

    print(f"  Detected classes: {train_dataset.classes}")

    # Load pretrained MobileNetV2
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    for param in model.features.parameters():
        param.requires_grad = False  # Freeze backbone

    # Replace classifier head for binary prediction (Normal vs Pneumonia)
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
    optimizer = optim.Adam(model.classifier.parameters(), lr=1e-4)

    epochs = 10
    best_acc = 0.0
    out_model_path = os.path.join(CURRENT_DIR, "chest_xray_model.pt")

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * inputs.size(0)

        # Validation
        model.eval()
        val_corrects = 0
        total_val = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                val_corrects += torch.sum(preds == labels.data).item()
                total_val += labels.size(0)

        val_acc = (val_corrects / total_val) * 100.0 if total_val else 0.0
        print(f"  Epoch [{epoch+1}/{epochs}] Loss: {running_loss/len(train_dataset):.4f} | Val Accuracy: {val_acc:.2f}%")

        if val_acc >= best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), out_model_path)

    print(f"\n[Success] Best PyTorch model saved to: {out_model_path}")

def train_tensorflow():
    print("[AI Training] Running TensorFlow/Keras MobileNetV2 pipeline...")
    # Standard Keras training
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        rotation_range=15,
        zoom_range=0.15,
        horizontal_flip=True
    )
    val_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

    train_gen = train_datagen.flow_from_directory(TRAIN_DIR, target_size=(224, 224), batch_size=16, class_mode="binary")
    val_gen = val_datagen.flow_from_directory(VAL_DIR, target_size=(224, 224), batch_size=16, class_mode="binary")

    base = MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights="imagenet")
    base.trainable = False
    x = GlobalAveragePooling2D()(base.output)
    x = Dense(128, activation="relu")(x)
    x = Dropout(0.3)(x)
    out = Dense(1, activation="sigmoid")(x)
    model = Model(inputs=base.input, outputs=out)
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

    out_path = os.path.join(CURRENT_DIR, "chest_xray_model.h5")
    model.fit(train_gen, validation_data=val_gen, epochs=10)
    model.save(out_path)
    print(f"[Success] TensorFlow model saved to: {out_path}")

if __name__ == "__main__":
    if not os.path.exists(TRAIN_DIR):
        print(f"[Notice] Dataset directory not found at: {TRAIN_DIR}")
        print("To train on real clinical data, download the Kaggle Chest Pneumonia dataset.")
        sys.exit(0)

    if HAS_TORCH:
        train_pytorch()
    elif HAS_TF:
        train_tensorflow()
    else:
        print("[Error] Neither PyTorch nor TensorFlow is installed. Run: pip install -r requirements.txt")
