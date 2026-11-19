"""AgroAI Authentication & User-Specific Data Isolation Test Suite.

Verifies:
1. Demo account login success (Ramesh Patel / ramesh@agrofield.ai)
2. Login rejection on invalid password
3. Registration of new farmer accounts
4. Duplicate email prevention
5. Protected /me endpoint with Bearer token authentication
6. Rejection of unauthenticated requests on protected routes
7. User profile updates (location & language preferences)
8. User session logout and token revocation
9. Data Isolation: User A scans do not appear in User B's scan history or dashboard
"""

import sys
import json
import uuid
import urllib.request
import urllib.parse
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000/api/v1"

def api_request(endpoint, method="GET", data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp_body = resp.read().decode("utf-8")
            return resp.status, json.loads(resp_body) if resp_body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, {"detail": err_body}

def run_tests():
    print("=" * 75)
    print("AGROAI AUTHENTICATION & USER DATA ISOLATION VERIFICATION")
    print("=" * 75)

    passed = 0
    failed = 0

    # 1. Login with seeded Demo User
    print("\n[1/9] Testing Demo Farmer Login...")
    code, res = api_request("/auth/login", method="POST", data={
        "email": "ramesh@agrofield.ai",
        "password": "Password123!"
    })
    if code == 200 and "access_token" in res and res.get("user", {}).get("email") == "ramesh@agrofield.ai":
        print("  [PASS] Demo farmer authenticated successfully. Token received.")
        demo_token = res["access_token"]
        passed += 1
    else:
        print(f"  [FAIL] Expected 200, got {code}: {res}")
        failed += 1
        demo_token = None

    # 2. Login rejection with wrong password
    print("\n[2/9] Testing Invalid Password Rejection...")
    code, res = api_request("/auth/login", method="POST", data={
        "email": "ramesh@agrofield.ai",
        "password": "WrongPassword999!"
    })
    if code == 401:
        print(f"  [PASS] Invalid password correctly rejected (HTTP 401): {res.get('detail')}")
        passed += 1
    else:
        print(f"  [FAIL] Expected 401, got {code}: {res}")
        failed += 1

    # 3. Register a new unique user (Farmer Priya)
    print("\n[3/9] Testing New Farmer Registration...")
    unique_suffix = uuid.uuid4().hex[:6]
    priya_email = f"priya_{unique_suffix}@agrofield.ai"
    code, res = api_request("/auth/register", method="POST", data={
        "full_name": "Priya Sharma",
        "email": priya_email,
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
        "location": "Varanasi Bio-Plot 2, UP",
        "preferred_language": "Hindi (HI)"
    })
    if code == 201 and "access_token" in res and res.get("user", {}).get("email") == priya_email:
        print(f"  [PASS] Farmer '{res['user']['full_name']}' registered (ID: {res['user']['id']}).")
        priya_token = res["access_token"]
        priya_id = res["user"]["id"]
        passed += 1
    else:
        print(f"  [FAIL] Expected 201, got {code}: {res}")
        failed += 1
        priya_token = None
        priya_id = None

    # 4. Duplicate email registration rejection
    print("\n[4/9] Testing Duplicate Email Prevention...")
    code, res = api_request("/auth/register", method="POST", data={
        "full_name": "Priya Imposter",
        "email": priya_email,
        "password": "AnotherPassword123!"
    })
    if code == 400 and "already exists" in str(res).lower():
        print(f"  [PASS] Duplicate registration rejected (HTTP 400): {res.get('detail')}")
        passed += 1
    else:
        print(f"  [FAIL] Expected 400, got {code}: {res}")
        failed += 1

    # 5. Protected /me endpoint with Bearer token
    print("\n[5/9] Testing Protected /auth/me Endpoint...")
    code, res = api_request("/auth/me", method="GET", token=priya_token)
    if code == 200 and res.get("email") == priya_email:
        print(f"  [PASS] Token authenticated. Retrieved farmer profile: {res.get('full_name')}, Location: {res.get('location')}")
        passed += 1
    else:
        print(f"  [FAIL] Expected 200, got {code}: {res}")
        failed += 1

    # 6. Rejection of unauthenticated requests
    print("\n[6/9] Testing Unauthenticated Request Rejection...")
    code, res = api_request("/auth/me", method="GET", token=None)
    if code == 401:
        print(f"  [PASS] Unauthenticated request correctly blocked (HTTP 401): {res.get('detail')}")
        passed += 1
    else:
        print(f"  [FAIL] Expected 401, got {code}: {res}")
        failed += 1

    # 7. Update profile
    print("\n[7/9] Testing Profile Update...")
    code, res = api_request("/auth/profile", method="PUT", token=priya_token, data={
        "full_name": "Dr. Priya Sharma",
        "location": "Varanasi Smart Polyhouse, UP",
        "preferred_language": "English (EN)"
    })
    if code == 200 and res.get("full_name") == "Dr. Priya Sharma" and "Polyhouse" in res.get("location", ""):
        print(f"  [PASS] Profile updated: {res.get('full_name')} at {res.get('location')}")
        passed += 1
    else:
        print(f"  [FAIL] Expected 200, got {code}: {res}")
        failed += 1

    # 8. Data Isolation between User A (Ramesh) and User B (Priya)
    print("\n[8/9] Testing User Scan & Dashboard Data Isolation...")
    # Register Farmer Amit
    amit_email = f"amit_{uuid.uuid4().hex[:6]}@agrofield.ai"
    _, amit_res = api_request("/auth/register", method="POST", data={
        "full_name": "Amit Verma",
        "email": amit_email,
        "password": "Password123!"
    })
    amit_token = amit_res["access_token"]

    # Check Amit's initial scans (should be 0 because Amit hasn't scanned anything yet)
    code, amit_scans = api_request("/scans", method="GET", token=amit_token)
    code2, ramesh_scans = api_request("/scans", method="GET", token=demo_token)

    if code == 200 and len(amit_scans) == 0 and len(ramesh_scans) > 0:
        print(f"  [PASS] Scan isolation verified: Fresh user Amit has 0 scans; Ramesh has {len(ramesh_scans)} scans.")
        # Also check dashboard summaries
        _, amit_dash = api_request("/dashboard/summary", method="GET", token=amit_token)
        _, ramesh_dash = api_request("/dashboard/summary", method="GET", token=demo_token)
        amit_count = amit_dash.get("farm_overview", {}).get("total_scans_logged")
        ramesh_count = ramesh_dash.get("farm_overview", {}).get("total_scans_logged")
        assert amit_count == 0, f"Expected 0 for Amit, got {amit_count}"
        assert ramesh_count > 0, f"Expected > 0 for Ramesh, got {ramesh_count}"
        print(f"  [PASS] Dashboard isolation verified: Amit dashboard shows {amit_count} scans; Ramesh shows {ramesh_count} scans.")
        passed += 1
    else:
        print(f"  [FAIL] Isolation issue: Amit scans: {len(amit_scans)}, Ramesh scans: {len(ramesh_scans)}")
        failed += 1

    # 9. Session Logout
    print("\n[9/9] Testing Session Logout & Invalidation...")
    code, res = api_request("/auth/logout", method="POST", token=amit_token)
    assert code == 200, f"Logout failed: {res}"
    # Verify subsequent call with revoked token returns 401
    code_after, res_after = api_request("/auth/me", method="GET", token=amit_token)
    if code_after == 401:
        print(f"  [PASS] Session token successfully revoked on logout. Subsequent calls blocked with HTTP 401.")
        passed += 1
    else:
        print(f"  [FAIL] Expected 401 after logout, got {code_after}: {res_after}")
        failed += 1

    print("\n" + "=" * 75)
    print("AUTHENTICATION & ISOLATION VERIFICATION SUMMARY")
    print("=" * 75)
    print(f"Total Tests: 9, Passed: {passed}, Failed: {failed}")
    print("=" * 75)
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
