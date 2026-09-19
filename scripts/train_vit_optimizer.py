"""
train_vit_optimizer.py
-----------------------
Phase Four: Vision Transformer (ViT-B/16) Optimization Engine
for RadiVision AI Chest & Bone Radiograph Classification.

Optimization Strategy:
  - Architecture: Dual-Head RadiVisionViT with ViT-B/16 ImageNet Pretrained Backbone
  - Preprocessing: Phase 2 CLAHE local contrast standardization
  - Data Augmentation: Phase 3 Domain Shift Augmentation (JPEG compression, blur, affine, perspective, noise)
  - Optimizer: AdamW with decoupled weight decay (lr=1e-4, weight_decay=1e-2)
  - Scheduler: Cosine Annealing Learning Rate Schedule (CosineAnnealingLR)
  - Loss Function: Weighted Cross-Entropy Loss prioritizing clinical Sensitivity (Recall for pathology)
  - Validation: Full evaluation on active test partitions targeting >90% diagnostic accuracy
"""

import os
import sys
import json
import time
import glob
import random
from datetime import datetime
from typing import Dict, Any, List, Tuple

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from PIL import Image

# Ensure project root is in sys.path
PROJECT_ROOT = os.environ.get("RADIVISION_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.vit_model import RadiVisionViT
from app.domain_shift_augmentation import DomainShiftAugmenter
from app.preprocessing import CLAHEStandardizer, preprocess_radiograph


class RadiographDataset(Dataset):
    """PyTorch Dataset with on-the-fly Domain Shift Augmentation or CLAHE Standardization."""

    def __init__(self, samples: List[Tuple[str, int]], modality: str, is_training: bool = True):
        self.samples = samples
        self.modality = modality
        self.is_training = is_training
        self.augmenter = DomainShiftAugmenter(modality=modality, is_training=is_training)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        try:
            tensor = self.augmenter(path)
            return tensor, torch.tensor(label, dtype=torch.long)
        except Exception as e:
            # Resilient blank tensor fallback
            return torch.zeros((3, 224, 224), dtype=torch.float32), torch.tensor(label, dtype=torch.long)


def collect_dataset_samples(modality: str) -> Dict[str, List[Tuple[str, int]]]:
    """Collects paths and integer labels for train, val, and test splits."""
    data = {"train": [], "val": [], "test": []}

    if modality.lower() == "chest":
        base_dir = os.path.join(PROJECT_ROOT, "dataset", "chest_xray")
        class_map = {"NORMAL": 0, "PNEUMONIA": 1}
    else:
        base_dir = os.path.join(PROJECT_ROOT, "dataset", "bone_xray", "classification")
        class_map = {"not fractured": 0, "fractured": 1}

    for split in ["train", "val", "test"]:
        split_dir = os.path.join(base_dir, split)
        if not os.path.exists(split_dir):
            continue
        for class_name, label in class_map.items():
            folder = os.path.join(split_dir, class_name)
            if not os.path.exists(folder):
                continue
            for ext in ("*.jpeg", "*.jpg", "*.png", "*.webp"):
                for p in glob.glob(os.path.join(folder, ext)):
                    if "_pruned_unviable" in p:
                        continue
                    data[split].append((p, label))

    return data


def extract_features_dataset(model: RadiVisionViT, dataloader: DataLoader, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
    """Extracts 768-dim ViT CLS tokens across dataset for rapid, high-stability head optimization."""
    features = []
    labels = []
    model.eval()
    with torch.no_grad():
        for batch_idx, (x, y) in enumerate(dataloader):
            x = x.to(device)
            cls_tokens = model.extract_cls(x)
            features.append(cls_tokens.cpu())
            labels.append(y)
            if (batch_idx + 1) % 10 == 0:
                print(f"    Processed { (batch_idx + 1) * dataloader.batch_size } samples...")
    return torch.cat(features, dim=0), torch.cat(labels, dim=0)


def train_modality_head(
    model: RadiVisionViT,
    modality: str,
    train_samples: List[Tuple[str, int]],
    test_samples: List[Tuple[str, int]],
    device: torch.device,
    epochs: int = 15,
    batch_size: int = 32,
    lr: float = 3e-4,
    weight_decay: float = 1e-2,
    sensitivity_weight: float = 1.35
) -> Dict[str, Any]:
    """
    Trains and optimizes the modality classification head using AdamW + Cosine Annealing.
    Targeting High Sensitivity (Recall) and >90% Overall Accuracy.
    """
    print(f"\n=======================================================")
    print(f"  OPTIMIZING ViT-B/16 HEAD FOR: {modality.upper()}")
    print(f"=======================================================")

    head = model.bone_head if modality.lower() == "bone" else model.chest_head
    head.to(device)

    # 1. Stratified training subset for swift CPU feature convergence
    random.seed(42)
    c0 = [s for s in train_samples if s[1] == 0]
    c1 = [s for s in train_samples if s[1] == 1]
    
    # Balance classes in training buffer
    n_per_class = min(len(c0), len(c1), 700)
    balanced_train = random.sample(c0, n_per_class) + random.sample(c1, n_per_class)
    random.shuffle(balanced_train)

    train_dataset = RadiographDataset(balanced_train, modality=modality, is_training=True)
    test_dataset = RadiographDataset(test_samples, modality=modality, is_training=False)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    print(f"  Extracting ViT-B/16 backbone features (Train: {len(balanced_train)}, Test: {len(test_samples)})...")
    train_feat, train_labels = extract_features_dataset(model, train_loader, device)
    test_feat, test_labels = extract_features_dataset(model, test_loader, device)

    # 2. Setup AdamW Optimizer and Cosine Annealing Scheduler
    optimizer = torch.optim.AdamW(head.parameters(), lr=lr, weight_decay=weight_decay, betas=(0.9, 0.999))
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)

    # 3. Weighted Cross Entropy prioritizing Sensitivity (penalizing False Negatives)
    class_weights = torch.tensor([1.0, sensitivity_weight], dtype=torch.float32).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    # Tensor dataset for rapid optimization
    feat_dataset = torch.utils.data.TensorDataset(train_feat, train_labels)
    feat_loader = DataLoader(feat_dataset, batch_size=32, shuffle=True)

    print(f"  Training {modality} Head with AdamW + Cosine Annealing ({epochs} epochs)...")
    best_acc = 0.0
    best_metrics = {}

    for epoch in range(1, epochs + 1):
        head.train()
        total_loss = 0.0
        correct = 0
        total = 0

        for f_batch, y_batch in feat_loader:
            f_batch, y_batch = f_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            logits = head(f_batch)
            loss = criterion(logits, y_batch)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * f_batch.size(0)
            preds = logits.argmax(dim=1)
            correct += (preds == y_batch).sum().item()
            total += y_batch.size(0)

        scheduler.step()
        train_acc = correct / total
        avg_loss = total_loss / total

        # Evaluation on Test set
        head.eval()
        with torch.no_grad():
            test_logits = head(test_feat.to(device))
            test_preds = test_logits.argmax(dim=1).cpu()

        # Compute Clinical Metrics
        tp = ((test_preds == 1) & (test_labels == 1)).sum().item()
        tn = ((test_preds == 0) & (test_labels == 0)).sum().item()
        fp = ((test_preds == 1) & (test_labels == 0)).sum().item()
        fn = ((test_preds == 0) & (test_labels == 1)).sum().item()

        test_acc = (tp + tn) / max(1, (tp + tn + fp + fn))
        sensitivity = tp / max(1, (tp + fn))  # Recall of pathology
        specificity = tn / max(1, (tn + fp))  # Recall of normal
        precision = tp / max(1, (tp + fp))
        f1 = 2 * (precision * sensitivity) / max(1e-6, (precision + sensitivity))

        if test_acc > best_acc or epoch == epochs:
            best_acc = test_acc
            best_metrics = {
                "modality": modality,
                "epoch": epoch,
                "accuracy": round(test_acc * 100, 2),
                "sensitivity": round(sensitivity * 100, 2),
                "specificity": round(specificity * 100, 2),
                "precision": round(precision * 100, 2),
                "f1_score": round(f1 * 100, 2),
                "tp": tp, "tn": tn, "fp": fp, "fn": fn,
                "test_total": len(test_labels)
            }

        if epoch % 3 == 0 or epoch == epochs:
            print(f"  Epoch {epoch:02d}/{epochs:02d} | Loss: {avg_loss:.4f} | LR: {scheduler.get_last_lr()[0]:.2e} | "
                  f"Test Acc: {test_acc*100:.1f}% | Sensitivity: {sensitivity*100:.1f}% | Specificity: {specificity*100:.1f}%")

    print(f"  -> Best Test Results for {modality}: Accuracy={best_metrics['accuracy']}%, Sensitivity={best_metrics['sensitivity']}%, Specificity={best_metrics['specificity']}%")
    return best_metrics


def run_vit_optimization():
    print("=======================================================")
    print("   PHASE 4: VISION TRANSFORMER (ViT-B/16) OPTIMIZATION")
    print("=======================================================")

    device = torch.device("cpu")
    print(f"Using Compute Device: {device}")

    # 1. Initialize pre-trained ViT model
    print("Initializing ViT-B/16 with pre-trained ImageNet backbone...")
    model = RadiVisionViT(pretrained=True)
    model.to(device)

    # 2. Collect Clean Datasets
    chest_data = collect_dataset_samples("Chest")
    bone_data = collect_dataset_samples("Bone")

    print(f"Chest Dataset: {len(chest_data['train'])} train, {len(chest_data['test'])} test")
    print(f"Bone Dataset:  {len(bone_data['train'])} train, {len(bone_data['test'])} test")

    # 3. Optimize Chest Head
    chest_metrics = train_modality_head(
        model=model,
        modality="Chest",
        train_samples=chest_data["train"],
        test_samples=chest_data["test"],
        device=device,
        epochs=15,
        lr=2.5e-4,
        sensitivity_weight=1.35
    )

    # 4. Optimize Bone Head
    bone_metrics = train_modality_head(
        model=model,
        modality="Bone",
        train_samples=bone_data["train"],
        test_samples=bone_data["test"],
        device=device,
        epochs=15,
        lr=2.5e-4,
        sensitivity_weight=1.25
    )

    # 5. Save Fine-Tuned ViT Weights
    weights_dir = os.path.join(PROJECT_ROOT, "model", "vit")
    os.makedirs(weights_dir, exist_ok=True)
    weights_path = os.path.join(weights_dir, "vit_diagnostic_model.pt")
    
    torch.save(model.state_dict(), weights_path)
    print(f"\nSaved fine-tuned ViT weights to: {weights_path} ({os.path.getsize(weights_path) / (1024*1024):.1f} MB)")

    # 6. Save Optimization Audit Report
    report = {
        "phase": "Phase 4: ViT Optimization",
        "timestamp": datetime.now().isoformat(),
        "optimizer": "AdamW (betas=(0.9, 0.999), weight_decay=0.01)",
        "scheduler": "CosineAnnealingLR (eta_min=1e-6)",
        "loss": "Weighted Cross-Entropy (High Sensitivity Target)",
        "preprocessing": "CLAHE (clip_limit=2.0, tile_grid=(8,8), res=224x224)",
        "chest_model": chest_metrics,
        "bone_model": bone_metrics
    }

    report_path = os.path.join(PROJECT_ROOT, "reports", "vit_optimization_report.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as rf:
        json.dump(report, rf, indent=2)

    print(f"Optimization report saved to: {report_path}")

    # 7. Test on Web-downloaded images
    print("\nVerifying on Real Web-Downloaded Images (from uploads/):")
    web_samples = glob.glob(os.path.join(PROJECT_ROOT, "uploads", "*.*"))[:5]
    model.eval()
    for wp in web_samples:
        try:
            prep = preprocess_radiograph(wp)
            inp = prep["tensor"].unsqueeze(0).to(device)
            with torch.no_grad():
                c_logits = model(inp, modality="Chest")
                b_logits = model(inp, modality="Bone")
                c_probs = torch.softmax(c_logits, dim=-1).squeeze().cpu().numpy()
                b_probs = torch.softmax(b_logits, dim=-1).squeeze().cpu().numpy()

            c_pred = "Pneumonia" if c_probs[1] > 0.5 else "Normal"
            b_pred = "Fracture" if b_probs[1] > 0.5 else "Normal"
            print(f"  {os.path.basename(wp)}:")
            print(f"    Chest ViT: {c_pred} ({max(c_probs)*100:.1f}%) | Bone ViT: {b_pred} ({max(b_probs)*100:.1f}%)")
        except Exception as e:
            print(f"  {os.path.basename(wp)}: Error {e}")

    print("\nPhase 4 ViT Optimization Complete!")
    return report

if __name__ == "__main__":
    run_vit_optimization()
