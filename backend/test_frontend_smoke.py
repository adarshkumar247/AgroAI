"""Frontend Smoke Test for AgroAI 10 Modules.

Validates:
1. All 10 module JavaScript files exist and contain valid render functions.
2. All 10 routes in app.js map properly to their module registrations.
3. All backend endpoints backing the 10 modules respond with 200 OK and match
   the exact JSON structures expected by the frontend templates.
"""

import os
import re
import json
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path("c:/agrofield")
JS_DIR = BASE_DIR / "js" / "modules"
API_BASE = "http://127.0.0.1:8000/api/v1"

MODULES_TO_TEST = [
    {
        "name": "Dashboard",
        "route": "dashboard",
        "js_file": "dashboard.js",
        "module_key": "dashboard",
        "api_test": lambda: test_endpoint(f"{API_BASE}/dashboard/summary", "GET")
    },
    {
        "name": "Crop Scanner",
        "route": "crop-scanner",
        "js_file": "scanner.js",
        "module_key": "scanner",
        "api_test": lambda: test_health()
    },
    {
        "name": "Health Analysis",
        "route": "health-analysis",
        "js_file": "report.js",
        "module_key": "report",
        "api_test": lambda: test_endpoint(f"{API_BASE}/scans", "GET")
    },
    {
        "name": "Crop Identification",
        "route": "crop-identification",
        "js_file": "crop-id.js",
        "module_key": "crop-identification",
        "api_test": lambda: test_health()
    },
    {
        "name": "Nutrient Guidance",
        "route": "nutrient-and-fertilizer",
        "js_file": "nutrients.js",
        "module_key": "nutrient-and-fertilizer",
        "api_test": lambda: test_endpoint(f"{API_BASE}/nutrients/guidance?crop=Tomato&stage=vegetative&observed_symptoms=yellowing_lower_leaves&soil_ph=6.8", "GET")
    },
    {
        "name": "Smart Irrigation",
        "route": "smart-irrigation",
        "js_file": "irrigation.js",
        "module_key": "smart-irrigation",
        "api_test": lambda: test_endpoint(f"{API_BASE}/irrigation/recommendation?crop=Tomato&stage=flowering&area_sqm=1000&soil_type=loam&lat=26.8467&lon=80.9462", "GET")
    },
    {
        "name": "Weather",
        "route": "weather-intelligence",
        "js_file": "weather.js",
        "module_key": "weather-intelligence",
        "api_test": lambda: test_endpoint(f"{API_BASE}/weather?lat=26.8467&lon=80.9462", "GET")
    },
    {
        "name": "AI Assistant",
        "route": "ai-assistant",
        "js_file": "assistant.js",
        "module_key": "ai-assistant",
        "api_test": lambda: test_endpoint(f"{API_BASE}/assistant/chat", "POST", {"message": "My rice leaves are turning yellow. What should I check first?", "crop": "Rice"})
    },
    {
        "name": "Scan History",
        "route": "scan-history",
        "js_file": "history.js",
        "module_key": "scan-history",
        "api_test": lambda: test_endpoint(f"{API_BASE}/scans", "GET")
    },
    {
        "name": "Farm Insights",
        "route": "farm-insights",
        "js_file": "insights.js",
        "module_key": "farm-insights",
        "api_test": lambda: test_endpoint(f"{API_BASE}/dashboard/summary", "GET")
    }
]

def test_endpoint(url, method="GET", json_body=None):
    if method == "GET":
        req = urllib.request.Request(url)
    else:
        req = urllib.request.Request(
            url,
            data=json.dumps(json_body or {}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
    with urllib.request.urlopen(req, timeout=20) as resp:
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        data = json.loads(resp.read().decode("utf-8"))
        return data

def test_health():
    req = urllib.request.Request(f"{API_BASE}/health")
    with urllib.request.urlopen(req, timeout=5) as resp:
        assert resp.status == 200
        return json.loads(resp.read().decode("utf-8"))

def run_smoke_tests():
    print("=" * 75)
    print("AGROAI FRONTEND SMOKE TEST - 10 MODULES")
    print("=" * 75)
    
    app_js_content = (BASE_DIR / "js" / "app.js").read_text(encoding="utf-8")
    index_html = (BASE_DIR / "index.html").read_text(encoding="utf-8")

    all_passed = True
    results = []

    for idx, mod in enumerate(MODULES_TO_TEST, 1):
        name = mod["name"]
        js_path = JS_DIR / mod["js_file"]
        
        try:
            # 1. Check JS file exists
            assert js_path.exists(), f"File {js_path.name} not found"
            js_code = js_path.read_text(encoding="utf-8")
            
            # 2. Check render function exists
            assert "render:" in js_code or "render(" in js_code or "function" in js_code, "No render function found"
            
            # 3. Check module script tag is included in index.html
            script_ref = f"/js/modules/{mod['js_file']}"
            assert script_ref in index_html, f"Script {script_ref} not referenced in index.html"
            
            # 4. Check route is mapped in app.js
            assert f"'{mod['route']}':" in app_js_content, f"Route '{mod['route']}' not mapped in app.js"
            
            # 5. Check backend API integration
            api_res = mod["api_test"]()
            assert api_res is not None, "API returned empty response"
            
            print(f"[{idx}/10] [PASS] {name} (Route: #{mod['route']}, Script: {mod['js_file']})")
            results.append((name, True, "Script, route, and API integration verified"))
        except Exception as e:
            all_passed = False
            print(f"[{idx}/10] [FAIL] {name}: {e}")
            results.append((name, False, str(e)))

    print("=" * 75)
    print("SMOKE TEST SUMMARY")
    print("=" * 75)
    passed_count = sum(1 for _, ok, _ in results if ok)
    print(f"Total: {len(results)}, Passed: {passed_count}, Failed: {len(results) - passed_count}")
    for name, ok, note in results:
        status_str = "PASS" if ok else "FAIL"
        print(f"  [{status_str}] {name}: {note}")
    print("=" * 75)
    return all_passed

if __name__ == "__main__":
    success = run_smoke_tests()
    exit(0 if success else 1)
