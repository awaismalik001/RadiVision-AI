"""
train_type_classifier.py
-------------------------
Trains a lightweight 3-class CNN to automatically classify incoming radiographs
into anatomical modalities: Chest, Bone, or Dental.
"""

import os
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset", "xray_type")
MODEL_OUT = os.path.join(CURRENT_DIR, "xray_type_classifier.h5")

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 15

def build_classifier():
    model = models.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        layers.MaxPooling2D((2, 2)),
        
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(3, activation='softmax')  # 3 classes: Bone, Chest, Dental
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

def train():
    if not os.path.exists(DATASET_DIR):
        print(f"[Error] Modality dataset directory not found at: {DATASET_DIR}")
        print("Please ensure dataset/xray_type contains 'chest', 'bone', and 'dental' subfolders.")
        return

    datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=15,
        zoom_range=0.15,
        horizontal_flip=True,
        validation_split=0.2
    )

    train_gen = datagen.flow_from_directory(
        DATASET_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training'
    )

    val_gen = datagen.flow_from_directory(
        DATASET_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation'
    )

    print(f"[AI Modality] Detected Class Mapping: {train_gen.class_indices}")

    model = build_classifier()
    model.summary()

    callbacks = [
        EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True),
        ModelCheckpoint(MODEL_OUT, monitor='val_accuracy', save_best_only=True, verbose=1)
    ]

    print("\n[AI Modality] Training modality classifier...")
    model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS,
        callbacks=callbacks
    )

    model.save(MODEL_OUT)
    print(f"\n[Success] Modality classifier exported to: {MODEL_OUT}")

if __name__ == "__main__":
    train()
