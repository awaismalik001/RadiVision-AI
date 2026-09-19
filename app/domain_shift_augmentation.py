"""
domain_shift_augmentation.py
----------------------------
Phase Three: Domain Shift Augmentation Pipeline
for RadiVision AI Vision Transformer Training.

Simulates the distribution shift observed when deploying clinical models to arbitrary
web-downloaded radiographs (JPEG compression artifacts, lens blur, perspective tilt,
sensor noise, lighting variations, and aspect ratio jitter).

Integrated with Phase 2 CLAHE standardization to produce robust, invariant representations.
"""

import io
import random
import cv2
import numpy as np
import torch
import torchvision.transforms as T
from PIL import Image
from typing import Tuple, Dict, Any, Optional, Union

from app.preprocessing import (
    CLAHEStandardizer,
    load_normalized_radiograph,
    VIT_INPUT_SIZE,
    IMAGENET_MEAN,
    IMAGENET_STD
)


class SimulatedJPEGCompression:
    """
    Simulates lossy web JPEG compression with random quality factors (30-80).
    Introduces 8x8 DCT quantization blockiness typical of web-downloaded images.
    """
    def __init__(self, quality_range: Tuple[int, int] = (35, 75), p: float = 0.6):
        self.quality_range = quality_range
        self.p = p

    def __call__(self, img: Image.Image) -> Image.Image:
        if random.random() > self.p:
            return img
        quality = random.randint(self.quality_range[0], self.quality_range[1])
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        buf.seek(0)
        return Image.open(buf).convert("RGB")


class AdditiveGaussianNoise:
    """
    Simulates high-ISO camera sensor noise, digitized film grain, and low-dose quantum mottle.
    Applied in tensor space: N(0, sigma^2).
    """
    def __init__(self, std_range: Tuple[float, float] = (0.01, 0.04), p: float = 0.35):
        self.std_range = std_range
        self.p = p

    def __call__(self, tensor: torch.Tensor) -> torch.Tensor:
        if random.random() > self.p:
            return tensor
        std = random.uniform(self.std_range[0], self.std_range[1])
        noise = torch.randn_like(tensor) * std
        return torch.clamp(tensor + noise, -3.0, 3.0)


class DomainShiftAugmenter:
    """
    Unified geometric and photometric degradation engine.
    Applies random affine, perspective, JPEG compression, blur, and noise,
    followed by CLAHE standardization to teach the ViT invariant representations.
    """

    def __init__(
        self,
        modality: str = "Chest",
        is_training: bool = True,
        clip_limit: float = 2.0,
        target_size: Tuple[int, int] = VIT_INPUT_SIZE
    ):
        self.modality = modality.lower()
        self.is_training = is_training
        self.standardizer = CLAHEStandardizer(
            clip_limit=clip_limit,
            tile_grid_size=(8, 8),
            target_size=target_size,
            preserve_aspect=False,
            normalize_tensor=True
        )

        if self.is_training:
            # 1. Geometric shifts
            geom_list = [
                T.RandomRotation(degrees=12),
                T.RandomAffine(degrees=0, translate=(0.06, 0.06), scale=(0.92, 1.08)),
                T.RandomPerspective(distortion_scale=0.15, p=0.4)
            ]
            if "bone" in self.modality:
                # Bone radiographs (arms, legs, hands) are horizontally symmetric
                geom_list.append(T.RandomHorizontalFlip(p=0.5))

            self.geom_transforms = T.Compose(geom_list)

            # 2. Photometric shifts (Web artifacts)
            self.jpeg_compress = SimulatedJPEGCompression(quality_range=(35, 75), p=0.6)
            self.color_jitter = T.ColorJitter(brightness=0.25, contrast=0.25)
            self.blur = T.GaussianBlur(kernel_size=3, sigma=(0.4, 1.2))
            self.noise = AdditiveGaussianNoise(std_range=(0.01, 0.04), p=0.35)

    def __call__(self, img_input: Union[str, Image.Image, np.ndarray]) -> torch.Tensor:
        """
        Executes domain shift augmentation on training images, or direct standardization on eval images.
        Returns normalized PyTorch Tensor (3, 224, 224).
        """
        if not self.is_training:
            return self.standardizer.process(img_input)["tensor"]

        # Ensure PIL Image
        if isinstance(img_input, str):
            with Image.open(img_input) as raw:
                img_pil = raw.convert("RGB")
        elif isinstance(img_input, np.ndarray):
            img_pil = Image.fromarray(load_normalized_radiograph(img_input))
        else:
            img_pil = img_input.convert("RGB")

        # 1. Apply geometric domain shift
        augmented_pil = self.geom_transforms(img_pil)

        # 2. Apply photometric web degradation
        augmented_pil = self.jpeg_compress(augmented_pil)
        if random.random() < 0.5:
            augmented_pil = self.color_jitter(augmented_pil)
        if random.random() < 0.35:
            augmented_pil = self.blur(augmented_pil)

        # 3. Apply CLAHE standardization to regularize the degraded input
        std_result = self.standardizer.process(augmented_pil)
        tensor = std_result["tensor"]

        # 4. Inject subtle sensor noise in tensor space
        tensor = self.noise(tensor)
        return tensor


def get_vit_domain_shift_transforms(modality: str = "Chest", is_training: bool = True):
    """Factory helper to retrieve domain shift augmentations for PyTorch DataLoaders."""
    return DomainShiftAugmenter(modality=modality, is_training=is_training)
