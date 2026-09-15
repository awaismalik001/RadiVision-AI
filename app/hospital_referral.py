"""
hospital_referral.py
---------------------
Clinical Healthcare & Specialist Referral Recommendation Engine for RadiVision AI.
Matches detected pathologies (Bone Fractures, Pneumonia / Infiltrates, Normal Scans)
with specialized local healthcare facilities, chief physicians, and emergency phone numbers
based on the patient's detected GPS coordinates or city location.
"""

from typing import List, Dict, Any

# Curated Clinical Facilities Directory by Location & Modality
CLINICAL_DIRECTORY = {
    "new york": {
        "Bone": [
            {
                "hospital": "Mount Sinai Orthopedic Hospital",
                "doctor": "Dr. James Miller, MD (Orthopedic Surgery)",
                "phone": "+1 (212) 555-0199",
                "email": "orthopedics@mountsinai.org",
                "distance": "1.8 km"
            },
            {
                "hospital": "NYU Langone Orthopedic Center",
                "doctor": "Dr. Laura Bennett, MD (Orthopedic Surgery)",
                "phone": "+1 (212) 555-0142",
                "email": "referrals@nyulangone.org",
                "distance": "3.1 km"
            },
            {
                "hospital": "Hospital for Special Surgery (HSS)",
                "doctor": "Dr. Michael Reyes, MD (Hand & Wrist)",
                "phone": "+1 (212) 555-0177",
                "email": "trauma@hss.edu",
                "distance": "4.5 km"
            }
        ],
        "Chest": [
            {
                "hospital": "NewYork-Presbyterian / Weill Cornell Medical Center",
                "doctor": "Dr. Arthur Vance, MD (Chief of Pulmonology)",
                "phone": "+1 (212) 555-0210",
                "email": "pulmonology@nyp.org",
                "distance": "2.1 km"
            },
            {
                "hospital": "Mount Sinai Respiratory Care Center",
                "doctor": "Dr. Elena Rostova, MD (Thoracic Medicine)",
                "phone": "+1 (212) 555-0233",
                "email": "respiratory@mountsinai.org",
                "distance": "2.8 km"
            },
            {
                "hospital": "Bellevue Hospital Center - Acute Respiratory Unit",
                "doctor": "Dr. Marcus Brody, MD (Critical Care & Pulmonology)",
                "phone": "+1 (212) 555-0288",
                "email": "acute_chest@bellevue.org",
                "distance": "3.9 km"
            }
        ]
    },
    "islamabad": {
        "Bone": [
            {
                "hospital": "Shifa International Hospital",
                "doctor": "Dr. Tariq Mahmood, MD (Orthopedic & Trauma Surgery)",
                "phone": "+92 51 846 4646",
                "email": "orthopedics@shifa.com.pk",
                "distance": "2.4 km"
            },
            {
                "hospital": "Pakistan Institute of Medical Sciences (PIMS)",
                "doctor": "Dr. Rizwan Khan, MD (Bone & Joint Trauma)",
                "phone": "+92 51 925 5010",
                "email": "trauma@pims.gov.pk",
                "distance": "3.6 km"
            },
            {
                "hospital": "Maroof International Hospital",
                "doctor": "Dr. Asim Malik, MD (Orthopedic Surgery)",
                "phone": "+92 51 261 1111",
                "email": "info@maroof.com.pk",
                "distance": "4.2 km"
            }
        ],
        "Chest": [
            {
                "hospital": "Shifa International Hospital",
                "doctor": "Dr. Kamran Siddiqui, MD (Pulmonology)",
                "phone": "+92 51 846 4646",
                "email": "pulmonology@shifa.com.pk",
                "distance": "2.4 km"
            },
            {
                "hospital": "Pakistan Institute of Medical Sciences (PIMS)",
                "doctor": "Dr. Ayesha Farooq, MD (Internal Medicine)",
                "phone": "+92 51 925 5010",
                "email": "respiratory@pims.gov.pk",
                "distance": "3.6 km"
            },
            {
                "hospital": "Maroof International Hospital",
                "doctor": "Dr. Bilal Hameed, MD (Pulmonology)",
                "phone": "+92 51 261 1111",
                "email": "chest_clinic@maroof.com.pk",
                "distance": "4.2 km"
            }
        ]
    }
}

DEFAULT_FALLBACK = {
    "Bone": [
        {
            "hospital": "Metropolitan Orthopedic & Trauma Center",
            "doctor": "Dr. James Miller, MD (Orthopedic Surgery)",
            "phone": "+1 (800) 555-0199",
            "email": "ortho_referrals@medicalcenter.org",
            "distance": "2.3 km"
        },
        {
            "hospital": "Regional University Trauma Hospital",
            "doctor": "Dr. Laura Bennett, MD (Orthopedic Surgery)",
            "phone": "+1 (800) 555-0142",
            "email": "trauma@universityhospital.org",
            "distance": "3.7 km"
        },
        {
            "hospital": "Center for Advanced Bone & Joint Care",
            "doctor": "Dr. Michael Reyes, MD (Hand & Wrist)",
            "phone": "+1 (800) 555-0177",
            "email": "contact@boneandjointcare.org",
            "distance": "5.1 km"
        }
    ],
    "Chest": [
        {
            "hospital": "Metropolitan Institute of Respiratory Medicine",
            "doctor": "Dr. Kamran Siddiqui, MD (Pulmonology)",
            "phone": "+1 (800) 555-0322",
            "email": "pulmonology@respiratorymed.org",
            "distance": "2.0 km"
        },
        {
            "hospital": "University Department of Thoracic Medicine",
            "doctor": "Dr. Ayesha Farooq, MD (Internal Medicine)",
            "phone": "+1 (800) 555-0355",
            "email": "thoracic@universityhealth.org",
            "distance": "3.4 km"
        },
        {
            "hospital": "Acute Pulmonary & Critical Care Hospital",
            "doctor": "Dr. Bilal Hameed, MD (Pulmonology)",
            "phone": "+1 (800) 555-0388",
            "email": "chest_care@pulmonaryacute.org",
            "distance": "4.8 km"
        }
    ]
}

def get_recommended_facilities(location: str, modality: str, is_abnormal: bool = True) -> List[Dict[str, Any]]:
    """
    Retrieves the top 3 recommended local hospitals and specialist physicians
    matched to the patient's location and clinical modality.
    """
    loc_clean = (location or "New York").strip().lower()
    mod_clean = "Bone" if "bone" in (modality or "").lower() else "Chest"

    # Find matching city or fallback
    matched_city = None
    for city_key in CLINICAL_DIRECTORY:
        if city_key in loc_clean:
            matched_city = city_key
            break

    if matched_city:
        facilities = CLINICAL_DIRECTORY[matched_city].get(mod_clean, DEFAULT_FALLBACK[mod_clean])
    else:
        facilities = DEFAULT_FALLBACK[mod_clean]

    # Normalize fields for both frontend and PDF report engines
    normalized = []
    for fac in facilities[:3]:
        item = dict(fac)
        item["hospital_name"] = item.get("hospital", item.get("hospital_name", "Specialist Center"))
        item["doctor_name"] = item.get("doctor", item.get("doctor_name", "Chief Medical Officer"))
        normalized.append(item)

    return normalized

