import sys
import os
import json
import urllib.request
import urllib.parse
from pathlib import Path
import uuid

BASE_URL = "http://127.0.0.1:8000"

def post_multipart(url, fields, files):
    boundary = uuid.uuid4().hex
    body = bytearray()

    for k, v in fields.items():
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode("utf-8"))
        body.extend(f"{v}\r\n".encode("utf-8"))

    for k, (filename, filedata, content_type) in files.items():
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{k}"; filename="{filename}"\r\n'.encode("utf-8"))
        body.extend(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
        body.extend(filedata)
        body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(url, data=bytes(body))
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req) as resp:
        return resp.getcode(), json.loads(resp.read().decode("utf-8"))

def get_json(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return resp.getcode(), json.loads(resp.read().decode("utf-8"))

def post_json(url, data):
    raw = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=raw)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return resp.getcode(), json.loads(resp.read().decode("utf-8"))

def run_e2e_test():
    print("=" * 70)
    print("AGROAI PLATFORM - FULL END-TO-END FLOW VERIFICATION")
    print("=" * 70)

    # -------------------------------------------------------------
    # FLOW 1: Crop Image -> Disease Model -> Result -> SQLite -> History -> Dashboard
    # -------------------------------------------------------------
    print("\n--- [FLOW 1] Crop Leaf Scan -> MobileNetV3 -> SQLite -> History -> Dashboard ---")
    
    test_img_path = Path("c:/agrofield/backend/data/raw/Tomato___Early_blight/image (1).JPG")
    if not test_img_path.exists():
        jpgs = list(Path("c:/agrofield/backend/data").glob("**/*.JPG")) + list(Path("c:/agrofield/backend/data").glob("**/*.jpg"))
        if jpgs:
            test_img_path = jpgs[0]
        else:
            print("[FAIL] No dataset image found!")
            return False

    print(f"1.1 Uploading test leaf: {test_img_path.name}")
    with open(test_img_path, "rb") as f:
        file_bytes = f.read()

    status, scan_result = post_multipart(
        f"{BASE_URL}/api/v1/scans",
        fields={"crop": "Tomato", "symptoms": "Brown concentric rings on leaf"},
        files={"image": (test_img_path.name, file_bytes, "image/jpeg")}
    )
    
    assert status in (200, 201), f"Scan failed: {status}"
    scan_id = scan_result.get("scan_id")
    print(f"  -> Model Result: {scan_result.get('possible_issue')}")
    print(f"  -> Confidence: {scan_result.get('confidence'):.2%}")
    print(f"  -> Severity: {scan_result.get('severity')}")
    print(f"  -> Scan ID Generated: {scan_id}")

    # 1.2 Verify scan is saved in SQLite and appears in History
    print(f"1.2 Querying SQLite Scan Archive (GET /api/v1/scans)...")
    status, history_scans = get_json(f"{BASE_URL}/api/v1/scans")
    assert status == 200, f"History failed: {status}"
    matching = [s for s in history_scans if s["scan_id"] == scan_id]
    assert len(matching) > 0, f"Scan {scan_id} not found in SQLite history!"
    print(f"  -> Found scan {scan_id} in SQLite history (Total historical scans: {len(history_scans)})")

    # 1.3 Verify scan appears on Dashboard summary
    print(f"1.3 Querying Dashboard Summary (GET /api/v1/dashboard/summary)...")
    status, dash_data = get_json(f"{BASE_URL}/api/v1/dashboard/summary")
    assert status == 200, f"Dashboard failed: {status}"
    farm = dash_data.get("farm_overview", {})
    recent = dash_data.get("recent_activity", [])
    print(f"  -> Total scans logged in DB: {farm.get('total_scans_logged')}")
    print(f"  -> Foliar Health Score: {farm.get('foliar_health_score_pct')}%")
    print(f"  -> Attention Needed: {farm.get('attention_needed_count')}")
    assert any(s["scan_id"] == scan_id for s in recent), f"Scan {scan_id} not in dashboard recent activity!"
    print(f"  -> Confirmed: scan {scan_id} is present in Dashboard recent activity!")
    print("[PASS] Flow 1 completed successfully.")

    # -------------------------------------------------------------
    # FLOW 2: Farmer Question -> FastAPI -> Gemini -> Response
    # -------------------------------------------------------------
    print("\n--- [FLOW 2] Farmer Question -> FastAPI -> Gemini Assistant -> Response ---")
    question_payload = {
        "message": "What is the recommended treatment protocol for Early Blight on tomatoes before rain?",
        "crop": "Tomato",
        "location": "Lucknow Farm, Uttar Pradesh",
        "recent_disease_scan": f"{scan_result.get('possible_issue')} ({scan_result.get('confidence'):.1%})"
    }
    print(f"2.1 Sending question: '{question_payload['message']}'")
    status, chat_data = post_json(f"{BASE_URL}/api/v1/assistant/chat", question_payload)
    assert status == 200, f"Assistant chat failed: {status}"
    print(f"  -> Provider: {chat_data.get('provider')}")
    print(f"  -> Model: {chat_data.get('model')}")
    print(f"  -> Response Excerpt: {chat_data.get('response')[:180]}...")
    print("[PASS] Flow 2 completed successfully.")

    # -------------------------------------------------------------
    # FLOW 3: Location -> Open-Meteo -> Weather -> Dashboard & Irrigation
    # -------------------------------------------------------------
    print("\n--- [FLOW 3] Location -> Open-Meteo -> Weather -> Irrigation Context ---")
    lat, lon = 26.8467, 80.9462
    print(f"3.1 Querying Open-Meteo for coordinates ({lat}, {lon}) - Lucknow, UP")
    status, w_data = get_json(f"{BASE_URL}/api/v1/weather?lat={lat}&lon={lon}")
    assert status == 200, f"Weather failed: {status}"
    cur = w_data.get("current", {})
    advisory = w_data.get("spray_advisory", {})
    daily = w_data.get("daily_forecast", [])
    print(f"  -> Condition: {cur.get('condition_text')}")
    print(f"  -> Temperature: {cur.get('temperature_2m')} C")
    print(f"  -> Humidity: {cur.get('relative_humidity_2m')}%")
    print(f"  -> Wind Speed: {cur.get('wind_speed_10m')} km/h")
    print(f"  -> Spray Window: {advisory.get('recommended_window')} (Safe: {advisory.get('is_safe_to_spray')})")
    print(f"  -> Daily Forecast Days: {len(daily)} days retrieved")

    print(f"3.2 Applying weather context to FAO-56 Smart Irrigation...")
    status, irr_data = get_json(f"{BASE_URL}/api/v1/irrigation/recommendation?crop=Tomato&stage=flowering&area_sqm=1000&lat={lat}&lon={lon}")
    assert status == 200, f"Irrigation failed: {status}"
    print(f"  -> Reference ET0: {irr_data.get('et0_ref_mm')} mm/day")
    print(f"  -> Crop Coefficient Kc: {irr_data.get('crop_coefficient_kc')}")
    print(f"  -> Crop Water Loss ETc: {irr_data.get('etc_mm_per_day')} mm/day")
    print(f"  -> Total Water Required: {irr_data.get('total_water_liters')} Liters")
    print(f"  -> Recommended Drip Runtime: {irr_data.get('recommended_run_time_minutes')} minutes")
    print(f"  -> Sensor Attribution: {irr_data.get('sensor_attribution')}")
    assert "No IoT hardware telemetry detected" in irr_data.get("sensor_attribution")
    print("[PASS] Flow 3 completed successfully.")

    # -------------------------------------------------------------
    # FLOW 4: Crop Identification Verification
    # -------------------------------------------------------------
    print("\n--- [FLOW 4] Crop Botanical Identification ---")
    status, cid_data = post_multipart(
        f"{BASE_URL}/api/v1/crop-id/identify",
        fields={},
        files={"image": (test_img_path.name, file_bytes, "image/jpeg")}
    )
    assert status == 200, f"Crop ID failed: {status}"
    print(f"  -> Crop Identified: {cid_data.get('crop')}")
    print(f"  -> Botanical Name: {cid_data.get('botanical_name')}")
    print(f"  -> Family: {cid_data.get('family')}")
    print(f"  -> Confidence: {cid_data.get('confidence'):.2%}")
    print("[PASS] Flow 4 completed successfully.")

    # -------------------------------------------------------------
    # FLOW 5: Nutrient Guidance Verification
    # -------------------------------------------------------------
    print("\n--- [FLOW 5] Nutrient & Soil Nutrition Guidance ---")
    status, nut_data = get_json(f"{BASE_URL}/api/v1/nutrients/guidance?crop=Tomato&stage=vegetative&observed_symptoms=yellowing_lower_leaves&soil_ph=6.8")
    assert status == 200, f"Nutrient guidance failed: {status}"
    diag = nut_data.get("diagnosis", {})
    recs = nut_data.get("recommendations", {})
    print(f"  -> Diagnosis: {diag.get('detected_deficiency')}")
    print(f"  -> Synthetic Option: {recs.get('synthetic_option')}")
    print(f"  -> Organic Option: {recs.get('organic_option')}")
    print(f"  -> Disclaimer: {nut_data.get('disclaimer')}")
    assert "indicative agronomic baselines" in nut_data.get("disclaimer")
    print("[PASS] Flow 5 completed successfully.")

    print("\n" + "=" * 70)
    print("ALL AGROAI MODULES & END-TO-END FLOWS FULLY VERIFIED!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = run_e2e_test()
    sys.exit(0 if success else 1)
