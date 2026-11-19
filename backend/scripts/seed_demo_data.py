"""AgroAI Demo Data Seeder.

Creates the standard demo account and realistic field scans:
- Demo Farmer: Ramesh Patel (ramesh@agrofield.ai / Password123!)
- Location: Lucknow Farm, Uttar Pradesh
- Crops: Tomato, Paddy Rice, Maize, Potato
- Realistic pathology distribution and diagnostics

Run:
  python backend/scripts/seed_demo_data.py
"""

import os
import sys
from datetime import datetime, timedelta

# Ensure repo root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.database.session import SessionLocal, init_db, DEMO_USER_ID, DEMO_USER_EMAIL
from backend.app.models.user import User
from backend.app.models.scan import Scan
from backend.app.core.security import hash_password

DEMO_SCANS = [
    {
        "id": "scan_demo_01",
        "crop_name": "Tomato",
        "possible_issue": "Early Blight",
        "confidence": 0.942,
        "severity": "Moderate",
        "stage": "Stage 2 — Concentric Halo Spots",
        "pathogen": "Alternaria solani",
        "spread_risk": "Moderate (Foliar splash)",
        "canopy_loss": "4.2%",
        "immediate_action": "Prune symptomatic lower foliage, transition to drip irrigation, spray copper oxychloride (2.5g/L).",
        "hours_ago": 2
    },
    {
        "id": "scan_demo_02",
        "crop_name": "Paddy Rice",
        "possible_issue": "Healthy",
        "confidence": 0.985,
        "severity": "Optimal",
        "stage": "Active Tillering",
        "pathogen": "None Detected",
        "spread_risk": "Low",
        "canopy_loss": "0%",
        "immediate_action": "Maintain 3-5 cm standing water layer. Apply second split of nitrogen top-dressing.",
        "hours_ago": 8
    },
    {
        "id": "scan_demo_03",
        "crop_name": "Maize / Corn",
        "possible_issue": "Common Rust",
        "confidence": 0.961,
        "severity": "Mild",
        "stage": "Early Pustules on Mid-Canopy",
        "pathogen": "Puccinia sorghi",
        "spread_risk": "High if relative humidity > 90%",
        "canopy_loss": "2.8%",
        "immediate_action": "Scout surrounding rows. Foliar spray of Mancozeb (2g/L) if rust lesions advance upward.",
        "hours_ago": 24
    },
    {
        "id": "scan_demo_04",
        "crop_name": "Potato",
        "possible_issue": "Late Blight",
        "confidence": 0.893,
        "severity": "Critical",
        "stage": "Active Water-Soaked Lesions",
        "pathogen": "Phytophthora infestans",
        "spread_risk": "Severe (Cool wet conditions)",
        "canopy_loss": "8.5%",
        "immediate_action": "Immediately quarantine infected plants. Apply systemic Cymoxanil + Mancozeb.",
        "hours_ago": 36
    },
    {
        "id": "scan_demo_05",
        "crop_name": "Tomato",
        "possible_issue": "Healthy",
        "confidence": 0.978,
        "severity": "Optimal",
        "stage": "Flowering & Early Fruit Set",
        "pathogen": "None Detected",
        "spread_risk": "Low",
        "canopy_loss": "0%",
        "immediate_action": "Maintain balanced calcium & potassium feeding to prevent blossom-end rot.",
        "hours_ago": 48
    },
    {
        "id": "scan_demo_06",
        "crop_name": "Paddy Rice",
        "possible_issue": "Brown Spot",
        "confidence": 0.914,
        "severity": "Moderate",
        "stage": "Tillering Stress",
        "pathogen": "Bipolaris oryzae",
        "spread_risk": "Moderate",
        "canopy_loss": "3.6%",
        "immediate_action": "Top-dress with Muriate of Potash (MOP). Correct water deficit stress.",
        "hours_ago": 72
    }
]

def seed():
    print("[Seed] Initializing database...")
    init_db()
    db = SessionLocal()

    try:
        # 1. Upsert Demo User
        user = db.query(User).filter(User.email == DEMO_USER_EMAIL).first()
        if not user:
            user = User(
                id=DEMO_USER_ID,
                full_name="Ramesh Patel",
                email=DEMO_USER_EMAIL,
                password_hash=hash_password("Password123!"),
                location="Lucknow Farm, Uttar Pradesh",
                preferred_language="English (EN)",
                created_at=datetime.utcnow() - timedelta(days=60)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"[Seed] Created demo user: {user.full_name} ({user.email})")
        else:
            print(f"[Seed] Existing demo user found: {user.full_name} ({user.email})")

        # 2. Seed Realistic Scans for Demo User
        now = datetime.utcnow()
        for item in DEMO_SCANS:
            existing = db.query(Scan).filter(Scan.id == item["id"]).first()
            if not existing:
                scan = Scan(
                    id=item["id"],
                    user_id=user.id,
                    image_path=f"/uploads/{item['id']}.jpg",
                    crop_name=item["crop_name"],
                    possible_issue=item["possible_issue"],
                    confidence=item["confidence"],
                    severity=item["severity"],
                    stage=item["stage"],
                    pathogen=item["pathogen"],
                    spread_risk=item["spread_risk"],
                    canopy_loss=item["canopy_loss"],
                    immediate_action=item["immediate_action"],
                    created_at=now - timedelta(hours=item["hours_ago"])
                )
                db.add(scan)
                print(f"[Seed] Added demo scan: {item['id']} ({item['crop_name']} - {item['possible_issue']})")

        db.commit()
        print("[Seed] Demo seeding successfully completed!")
        print(f"  Demo Account Login: {DEMO_USER_EMAIL}")
        print(f"  Demo Account Password: Password123!")

    except Exception as e:
        db.rollback()
        print(f"[Seed] Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
