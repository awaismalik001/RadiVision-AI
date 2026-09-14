"""
evaluate_chest.py
-----------------
Comprehensive clinical evaluation suite for the RadiVision AI Chest Pneumonia Classifier.
Evaluates the model across the entire clinical test set (636 radiographs) and generates:
- Overall Accuracy
- Sensitivity / Recall (Abnormality detection rate)
- Specificity (Healthy confirmation rate)
- Precision & F1-Score
- Confusion Matrix (TP, TN, FP, FN)
- Publication-quality Confusion Matrix plot and ROC Curve plot
"""

import os
import sys
import numpy as np
import torch
import torch.nn as nn
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
import matplotlib.pyplot as plt

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
TEST_DIR = os.path.join(PROJECT_ROOT, "dataset", "chest_xray", "test")
MODEL_PATH = os.path.join(CURRENT_DIR, "chest_xray_model.pt")

def evaluate(save_plots: bool = True):
    print("=" * 65)
    print("       RadiVision AI: Clinical Chest Model Evaluation Suite")
    print("=" * 65)

    if not os.path.exists(TEST_DIR):
        print(f"[Error] Test dataset directory not found at: {TEST_DIR}")
        return

    if not os.path.exists(MODEL_PATH):
        print(f"[Error] Model weights not found at: {MODEL_PATH}")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Compute Device: {device}")
    print(f"Model Path    : {MODEL_PATH}")
    print(f"Test Dataset  : {TEST_DIR}\n")

    # Image transformations matching clinical inference
    test_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    test_dataset = datasets.ImageFolder(TEST_DIR, transform=test_transforms)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=0)

    class_names = test_dataset.classes  # ['NORMAL', 'PNEUMONIA']
    print(f"Detected Classes: {class_names}")
    print(f"Total Test Cases: {len(test_dataset)} images")

    # Load MobileNetV2 architecture
    model = models.mobilenet_v2(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, 128),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(128, 2)
    )
    
    state_dict = torch.load(MODEL_PATH, map_location=device)
    model.load_state_dict(state_dict)
    model = model.to(device)
    model.eval()

    all_preds = []
    all_targets = []
    all_probs = []

    print("\nRunning batch inference across test set...")
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            probs = torch.softmax(outputs, dim=1)
            preds = torch.argmax(probs, dim=1)

            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(targets.cpu().numpy())
            all_probs.extend(probs[:, 1].cpu().numpy())  # Pneumonia probability

    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)
    all_probs = np.array(all_probs)

    # Compute Clinical Metrics
    cm = confusion_matrix(all_targets, all_preds)
    tn, fp, fn, tp = cm.ravel()

    accuracy = (tp + tn) / float(tp + tn + fp + fn)
    sensitivity = tp / float(tp + fn) if (tp + fn) > 0 else 0.0  # Recall for Pneumonia
    specificity = tn / float(tn + fp) if (tn + fp) > 0 else 0.0  # Recall for Normal
    precision = tp / float(tp + fp) if (tp + fp) > 0 else 0.0
    f1 = 2 * (precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) > 0 else 0.0

    fpr, tpr, _ = roc_curve(all_targets, all_probs)
    roc_auc = auc(fpr, tpr)

    print("\n" + "=" * 65)
    print("                     CLINICAL PERFORMANCE REPORT")
    print("=" * 65)
    print(f"  Overall Accuracy        : {accuracy * 100:.2f}%")
    print(f"  Clinical Sensitivity    : {sensitivity * 100:.2f}% (Pneumonia detection)")
    print(f"  Clinical Specificity    : {specificity * 100:.2f}% (Normal lung confirmation)")
    print(f"  Precision (PPV)         : {precision * 100:.2f}%")
    print(f"  F1-Score                : {f1 * 100:.2f}%")
    print(f"  Area Under ROC (AUC)    : {roc_auc:.4f}")
    print("-" * 65)
    print(f"  True Positives  (TP)    : {tp}  (Correctly identified Pneumonia)")
    print(f"  True Negatives  (TN)    : {tn}  (Correctly identified Normal)")
    print(f"  False Positives (FP)    : {fp}  (Normal misclassified as Pneumonia)")
    print(f"  False Negatives (FN)    : {fn}  (Pneumonia misclassified as Normal)")
    print("=" * 65)

    if save_plots:
        # 1. Confusion Matrix Plot
        fig, ax = plt.subplots(figsize=(6, 5))
        cax = ax.matshow(cm, cmap=plt.cm.Blues, alpha=0.8)
        fig.colorbar(cax)
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(x=j, y=i, s=f"{cm[i, j]}", va='center', ha='center', size='xx-large', weight='bold')

        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(['NORMAL', 'PNEUMONIA'], fontsize=11, fontweight='bold')
        ax.set_yticklabels(['NORMAL', 'PNEUMONIA'], fontsize=11, fontweight='bold')
        ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
        ax.set_ylabel('Ground Truth Label', fontsize=12, fontweight='bold')
        ax.set_title(f'Confusion Matrix (Accuracy: {accuracy*100:.1f}%)', fontsize=13, fontweight='bold', pad=15)
        plt.tight_layout()
        cm_path = os.path.join(CURRENT_DIR, "confusion_matrix.png")
        plt.savefig(cm_path, dpi=200)
        plt.close()
        print(f"\n[Saved] Confusion Matrix plot: {cm_path}")

        # 2. ROC Curve Plot
        plt.figure(figsize=(6, 5))
        plt.plot(fpr, tpr, color='#0B3D66', lw=2.5, label=f'ROC curve (AUC = {roc_auc:.3f})')
        plt.plot([0, 1], [0, 1], color='#E24B4A', lw=1.5, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate (1 - Specificity)', fontsize=11, fontweight='bold')
        plt.ylabel('True Positive Rate (Sensitivity)', fontsize=11, fontweight='bold')
        plt.title('Receiver Operating Characteristic (ROC)', fontsize=12, fontweight='bold')
        plt.legend(loc="lower right", fontsize=10)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        roc_path = os.path.join(CURRENT_DIR, "roc_curve.png")
        plt.savefig(roc_path, dpi=200)
        plt.close()
        print(f"[Saved] ROC Curve plot: {roc_path}")

    return {
        "accuracy": accuracy,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "precision": precision,
        "f1": f1,
        "roc_auc": roc_auc,
        "confusion_matrix": cm.tolist()
    }

if __name__ == "__main__":
    evaluate()
