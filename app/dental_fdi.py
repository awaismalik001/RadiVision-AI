"""
dental_fdi.py
-------------
FDI World Dental Federation (ISO 3950) Two-Digit Tooth Numbering Engine.
Maps 2D spatial bounding box coordinates on panoramic dental radiographs
into clinical tooth identifiers across all 4 dental quadrants:
- Quadrant 1 (Maxillary Right): Teeth 18 to 11
- Quadrant 2 (Maxillary Left) : Teeth 21 to 28
- Quadrant 3 (Mandibular Left): Teeth 31 to 38
- Quadrant 4 (Mandibular Right): Teeth 48 to 41
"""

def map_coordinates_to_fdi(bx: float, by: float, bw: float, bh: float) -> str:
    """
    Computes the FDI two-digit tooth number based on normalized bounding box center.
    bx, by, bw, bh are in range [0.0, 1.0].
    Panoramic view convention:
    - Left side of image (viewer) = Patient's Right (Quadrants 1 & 4)
    - Right side of image (viewer) = Patient's Left (Quadrants 2 & 3)
    - Upper half (Y < 0.52) = Maxilla (Upper Jaw)
    - Lower half (Y >= 0.52) = Mandible (Lower Jaw)
    """
    center_x = bx + (bw / 2.0)
    center_y = by + (bh / 2.0)

    # 1. Determine Vertical Arch (Upper vs Lower Jaw)
    is_upper = (center_y < 0.52)

    # 2. Determine Horizontal Quadrant & Distance from Midline (0.50)
    # Midline is between central incisors (11/21 for upper, 41/31 for lower)
    dist_from_midline = abs(center_x - 0.50)
    # Map distance [0.0, 0.45] to tooth position [1 (central incisor) .. 8 (3rd molar)]
    tooth_pos = int(round((dist_from_midline / 0.45) * 7.0)) + 1
    tooth_pos = max(1, min(8, tooth_pos))

    if is_upper:
        if center_x <= 0.50:
            # Quadrant 1: Maxillary Right (Teeth 11 to 18)
            return str(10 + tooth_pos)
        else:
            # Quadrant 2: Maxillary Left (Teeth 21 to 28)
            return str(20 + tooth_pos)
    else:
        if center_x <= 0.50:
            # Quadrant 4: Mandibular Right (Teeth 41 to 48)
            return str(40 + tooth_pos)
        else:
            # Quadrant 3: Mandibular Left (Teeth 31 to 38)
            return str(30 + tooth_pos)

def format_pathology_label(cls_name: str, tooth_num: str) -> str:
    """Provides clinically accurate diagnostic labeling for detected pathologies."""
    name_clean = cls_name.replace("_", " ").title()
    if "Deep Caries" in name_clean:
        return f"Deep Dentinal Caries"
    elif "Caries" in name_clean:
        return f"Coronal / Enamel Caries"
    elif "Periapical" in name_clean:
        return f"Periapical Radiolucency"
    elif "Impacted" in name_clean:
        return f"Impacted Molar"
    elif "Healthy" in name_clean:
        return f"Erupted Tooth (Intact)"
    return name_clean
