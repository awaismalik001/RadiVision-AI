"""
preprocessing.py
----------------
Phase Two: Standardization & CLAHE Preprocessing Pipeline
for RadiVision AI Vision Transformer (ViT-B/16).

Provides:
  1. Contrast Limited Adaptive Histogram Equalization (CLAHE) with tile-based local contrast expansion.
  2. Resolution standardization to ViT-B/16 target spatial dimension (224 x 224).
  3. Robust channel harmonization (transparency stripping, palette handling, 3-channel ViT replication).
  4. PyTorch-compatible Transform (`ViTStandardizationTransform`) for Training DataLoaders and Live Inference.
"""

import io
import cv2
import numpy as np
import torch
from PIL import Image, ImageFile
from typing import Union, Tuple, Dict, Any, Optional

# Allow processing of high-resolution or web-downloaded image streams
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Standard ViT ImageNet calibration parameters
VIT_INPUT_SIZE = (224, 224)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def load_normalized_radiograph(img_input: Union[str, Image.Image, np.ndarray]) -> np.ndarray:
    """
    Loads an image from filepath, PIL Image, or NumPy array and normalizes to RGB uint8.
    Safely strips alpha channels by compositing on black background (standard radiograph background).
    """
    if isinstance(img_input, str):
        with Image.open(img_input) as raw_img:
            if raw_img.mode in ('RGBA', 'LA', 'P'):
                raw_img = raw_img.convert('RGBA')
                bg = Image.new('RGBA', raw_img.size, (0, 0, 0, 255))
                rgb_img = Image.alpha_composite(bg, raw_img).convert('RGB')
            else:
                rgb_img = raw_img.convert('RGB')
            return np.array(rgb_img)

    elif isinstance(img_input, Image.Image):
        if img_input.mode in ('RGBA', 'LA', 'P'):
            img_converted = img_input.convert('RGBA')
            bg = Image.new('RGBA', img_converted.size, (0, 0, 0, 255))
            rgb_img = Image.alpha_composite(bg, img_converted).convert('RGB')
        else:
            rgb_img = img_input.convert('RGB')
        return np.array(rgb_img)

    elif isinstance(img_input, np.ndarray):
        if len(img_input.shape) == 2:
            return cv2.cvtColor(img_input, cv2.COLOR_GRAY2RGB)
        elif img_input.shape[2] == 4:
            # Alpha composite
            rgb = img_input[:, :, :3]
            alpha = img_input[:, :, 3:4] / 255.0
            composite = (rgb * alpha).astype(np.uint8)
            return composite
        elif img_input.shape[2] == 3:
            return img_input.copy()
        else:
            raise ValueError(f"Unexpected image array shape: {img_input.shape}")

    else:
        raise TypeError(f"Unsupported image input type: {type(img_input)}")


class CLAHEStandardizer:
    """
    Standardizes radiographs via Contrast Limited Adaptive Histogram Equalization (CLAHE)
    and high-order spatial resizing for Vision Transformer architectures.
    """

    def __init__(
        self,
        clip_limit: float = 2.0,
        tile_grid_size: Tuple[int, int] = (8, 8),
        target_size: Tuple[int, int] = VIT_INPUT_SIZE,
        preserve_aspect: bool = False,
        normalize_tensor: bool = True
    ):
        self.clip_limit = clip_limit
        self.tile_grid_size = tile_grid_size
        self.target_size = target_size
        self.preserve_aspect = preserve_aspect
        self.normalize_tensor = normalize_tensor
        self.clahe = cv2.createCLAHE(clipLimit=self.clip_limit, tileGridSize=self.tile_grid_size)

        self.mean = torch.tensor(IMAGENET_MEAN, dtype=torch.float32).view(3, 1, 1)
        self.std = torch.tensor(IMAGENET_STD, dtype=torch.float32).view(3, 1, 1)

    def process(self, img_input: Union[str, Image.Image, np.ndarray]) -> Dict[str, Any]:
        """
        Executes full standardization pipeline:
          1. Color/alpha stripping to RGB
          2. Grayscale conversion
          3. CLAHE local adaptive contrast enhancement
          4. Bicubic resize to (224, 224)
          5. 3-channel replication for ViT attention heads
          6. PyTorch tensor normalization
        """
        rgb_np = load_normalized_radiograph(img_input)

        # Grayscale for radiographic density analysis
        gray = cv2.cvtColor(rgb_np, cv2.COLOR_RGB2GRAY)

        # Apply CLAHE
        clahe_gray = self.clahe.apply(gray)

        # Resize to ViT input dimension (224, 224)
        target_w, target_h = self.target_size
        if self.preserve_aspect:
            h, w = clahe_gray.shape[:2]
            scale = min(target_w / w, target_h / h)
            new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
            resized = cv2.resize(clahe_gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

            canvas = np.zeros((target_h, target_w), dtype=np.uint8)
            x_off = (target_w - new_w) // 2
            y_off = (target_h - new_h) // 2
            canvas[y_off:y_off + new_h, x_off:x_off + new_w] = resized
            standardized_gray = canvas
        else:
            standardized_gray = cv2.resize(clahe_gray, (target_w, target_h), interpolation=cv2.INTER_CUBIC)

        # 3-channel merge for ViT input
        standardized_rgb = cv2.merge([standardized_gray, standardized_gray, standardized_gray])
        pil_image = Image.fromarray(standardized_rgb)

        # PyTorch Tensor: (3, 224, 224)
        tensor = torch.from_numpy(standardized_rgb).permute(2, 0, 1).float() / 255.0
        if self.normalize_tensor:
            tensor = (tensor - self.mean) / self.std

        return {
            "pil_image": pil_image,
            "numpy_image": standardized_rgb,
            "tensor": tensor,
            "grayscale_clahe": standardized_gray,
            "resolution": self.target_size
        }


class ViTStandardizationTransform:
    """
    Torchvision-compatible callable transform for PyTorch Datasets and DataLoaders.
    Input: PIL Image or NumPy array
    Output: Normalized PyTorch Tensor (3, 224, 224)
    """

    def __init__(
        self,
        clip_limit: float = 2.0,
        tile_grid_size: Tuple[int, int] = (8, 8),
        target_size: Tuple[int, int] = VIT_INPUT_SIZE,
        preserve_aspect: bool = False
    ):
        self.standardizer = CLAHEStandardizer(
            clip_limit=clip_limit,
            tile_grid_size=tile_grid_size,
            target_size=target_size,
            preserve_aspect=preserve_aspect,
            normalize_tensor=True
        )

    def __call__(self, img: Union[Image.Image, np.ndarray]) -> torch.Tensor:
        res = self.standardizer.process(img)
        return res["tensor"]


# Default global standardizer instance
default_standardizer = CLAHEStandardizer(clip_limit=2.0, tile_grid_size=(8, 8))

def preprocess_radiograph(img_input: Union[str, Image.Image, np.ndarray]) -> Dict[str, Any]:
    """Convenience helper to apply default CLAHE standardization."""
    return default_standardizer.process(img_input)
