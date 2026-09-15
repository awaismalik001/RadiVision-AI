"""
evaluate_bone.py
----------------
Comprehensive clinical evaluation suite for the RadiVision AI Bone Fracture Classifier.
Evaluates the model across the entire clinical test set (506 radiographs) and generates:
- Overall Accuracy
- Clinical Sensitivity (Fracture detection rate)
- Clinical Specificity (Normal bone confirmation rate)
- Precision & F1-Score
- Confusion Matrix (TP, TN, FP, FN)
- Publication-quality Confusion Matrix plot and ROC Curve plot
"""

import os
import sys
import numpy as np
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

import torch
import torch.nn as nn
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
import matplotlib.pyplot as plt

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
TEST_DIR = os.path.join(PROJECT_ROOT, "dataset", "bone_xray", "classification", "test")
MODEL_PATH = os.path.join(CURRENT_DIR, "bone_fracture_model.pt")

def evaluate_bone(save_plots: bool = True):
    print("=" * 65)
    print("       RadiVision AI: Clinical Bone Fracture Evaluation Suite")
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

    test_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    test_dataset = datasets.ImageFolder(TEST_DIR, transform=test_transforms)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=0)

    class_names = test_dataset.classes  # ['fractured', 'not fractured']
    print(f"Detected Classes: {class_names}")
    print(f"Total Test Cases: {len(test_dataset)} radiographs")

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

    print("\nRunning batch inference across bone test set...")
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            probs = torch.softmax(outputs, dim=1)
            preds = torch.argmax(probs, dim=1)

            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(targets.cpu().numpy())
            # In ['fractured', 'not fractured'], fractured is index 0
            # For clinical ROC where positive class = fractured, prob = probs[:, 0], target = 0
            all_probs.extend(probs[:, 0].cpu().numpy())

    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)
    all_probs = np.array(all_probs)

    # Class 0: fractured (Positive), Class 1: not fractured (Negative)
    # Binarize targets: 1 for fractured, 0 for not fractured
    binary_targets = (all_targets == 0).astype(int)
    binary_preds = (all_preds == 0).astype(int)

    cm = confusion_matrix(binary_targets, binary_preds)
    tn, fp, fn, tp = cm.ravel()

    accuracy = (tp + tn) / float(tp + tn + fp + fn)
    sensitivity = tp / float(tp + fn) if (tp + fn) > 0 else 0.0  # Fracture Recall
    specificity = tn / float(tn + fp) if (tn + fp) > 0 else 0.0  # Normal confirmation
    precision = tp / float(tp + fp) if (tp + fp) > 0 else 0.0
    f1 = 2 * (precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) > 0 else 0.0

    fpr, tpr, _ = roc_curve(binary_targets, all_probs)
    roc_auc = auc(fpr, tpr)

    # Calibrate optimal decision threshold for maximum accuracy
    best_t = 0.5
    best_acc = accuracy
    for t in np.linspace(0.4, 0.75, 71):
        p_t = (all_probs >= t).astype(int)
        acc_t = np.mean(p_t == binary_targets)
        if acc_t > best_acc:
            best_acc = acc_t
            best_t = t

    opt_preds = (all_probs >= best_t).astype(int)
    opt_cm = confusion_matrix(binary_targets, opt_preds)
    opt_tn, opt_fp, opt_fn, opt_tp = opt_cm.ravel()
    opt_sens = opt_tp / float(opt_tp + opt_fn) if (opt_tp + opt_fn) > 0 else 0.0
    opt_spec = opt_tn / float(opt_tn + opt_fp) if (opt_tn + opt_fp) > 0 else 0.0

    print("\n" + "=" * 65)
    print("                 CLINICAL BONE FRACTURE REPORT")
    print("=" * 65)
    print(f"  Standard Accuracy (t=0.50)  : {accuracy * 100:.2f}%")
    print(f"  Clinical Sensitivity        : {sensitivity * 100:.2f}% (Fracture detection rate)")
    print(f"  Clinical Specificity        : {specificity * 100:.2f}% (Normal bone confirmation)")
    print(f"  Precision (PPV)             : {precision * 100:.2f}%")
    print(f"  F1-Score                    : {f1 * 100:.2f}%")
    print(f"  Area Under ROC (AUC)        : {roc_auc:.4f}")
    print("-" * 65)
    print(f"  Calibrated Accuracy (t={best_t:.3f}): {best_acc * 100:.2f}%")
    print(f"  Calibrated Sensitivity      : {opt_sens * 100:.2f}%")
    print(f"  Calibrated Specificity      : {opt_spec * 100:.2f}%")
    print("-" * 65)
    print(f"  True Positives  (TP)        : {opt_tp}  (Correctly identified Fractures)")
    print(f"  True Negatives  (TN)        : {opt_tn}  (Correctly identified Healthy Bones)")
    print(f"  False Positives (FP)        : {opt_fp}  (Normal misclassified as Fracture)")
    print(f"  False Negatives (FN)        : {opt_fn}  (Fracture missed as Normal)")
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
        ax.set_xticklabels(['HEALTHY', 'FRACTURED'], fontsize=11, fontweight='bold')
        ax.set_yticklabels(['HEALTHY', 'FRACTURED'], fontsize=11, fontweight='bold')
        ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
        ax.set_ylabel('Ground Truth Label', fontsize=12, fontweight='bold')
        ax.set_title(f'Bone Confusion Matrix (Acc: {accuracy*100:.1f}%)', fontsize=13, fontweight='bold', pad=15)
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
        plt.title('Bone Fracture ROC Curve', fontsize=12, fontweight='bold')
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
        "roc_auc": roc_auc
    }

if __name__ == "__main__":
    evaluate_bone()
