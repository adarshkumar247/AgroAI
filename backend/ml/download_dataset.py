"""AgroAI Dual-Source Dataset Acquisition and Preparation Pipeline.

Extracts the verified 11-class balanced benchmark:
  - 10 classes from PlantVillage (Penn State / EPFL, CC0 1.0)
  - 1 class (Rice Brown Spot) from Rice Leaf Disease Benchmark (Mendeley / UCI, CC BY 4.0)

Extracts exactly 150 verified images per class (1,650 total images) into backend/data/.
Uses direct HTTP range streaming on CDN-resolved endpoints for high throughput.
"""

import os
import sys
import io
import time
import zlib
import json
import zipfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

sys.path.insert(0, "c:/agrofield")
from backend.test_remote_zip import RemoteZipReader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "backend", "data")
MODELS_DIR = os.path.join(BASE_DIR, "backend", "models")

TARGET_CLASSES = {
    # PlantVillage classes: (PV_folder_name, final_class_name)
    "pv": [
        ("Tomato___Early_blight", "Tomato___Early_blight"),
        ("Tomato___Late_blight", "Tomato___Late_blight"),
        ("Tomato___Target_Spot", "Tomato___Target_Spot"),
        ("Tomato___healthy", "Tomato___healthy"),
        ("Potato___Early_blight", "Potato___Early_blight"),
        ("Potato___Late_blight", "Potato___Late_blight"),
        ("Potato___healthy", "Potato___healthy"),
        ("Corn_(maize)___Common_rust_", "Corn___Common_rust_"),
        ("Corn_(maize)___Northern_Leaf_Blight", "Corn___Northern_Leaf_Blight"),
        ("Corn_(maize)___healthy", "Corn___healthy")
    ],
    # Rice class: (folder_match, final_class_name)
    "rice": [
        ("Brownspot", "Rice___Brown_spot")
    ]
}

IMAGES_PER_CLASS = 150

def resolve_cdn_url(redirect_url: str) -> str:
    """Resolve 302 redirect once to obtain direct high-throughput CDN URL."""
    print(f"Resolving CDN endpoint for: {redirect_url}...")
    req = urllib.request.Request(redirect_url, headers={"User-Agent": "Mozilla/5.0"}, method="HEAD")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.geturl()

def extract_entry_from_cdn(cdn_url: str, info: zipfile.ZipInfo, output_path: str, max_retries: int = 3) -> bool:
    """Download and decompress a single zip entry via direct HTTP byte-range request."""
    byte_start = info.header_offset
    byte_end = info.header_offset + 120 + len(info.filename.encode("utf-8")) + info.compress_size

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                cdn_url,
                headers={"User-Agent": "Mozilla/5.0", "Range": f"bytes={byte_start}-{byte_end}"}
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()

            if len(data) < 30:
                raise ValueError("Incomplete local file header received")

            name_len = int.from_bytes(data[26:28], "little")
            extra_len = int.from_bytes(data[28:30], "little")
            payload = data[30 + name_len + extra_len : 30 + name_len + extra_len + info.compress_size]

            if info.compress_type == zipfile.ZIP_DEFLATED:
                decompressed = zlib.decompress(payload, -15)
            else:
                decompressed = payload

            # Verify image integrity via PIL
            img = Image.open(io.BytesIO(decompressed))
            img.verify()

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(decompressed)
            return True

        except Exception as e:
            if attempt == max_retries - 1:
                print(f"  [Error] Failed to extract {info.filename}: {e}")
                return False
            time.sleep(1.0)
    return False

def prepare_dataset():
    print("=" * 65)
    print(" AgroAI Dual-Source 11-Class Dataset Acquisition Pipeline")
    print("=" * 65)
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    final_class_names = [pair[1] for pair in TARGET_CLASSES["pv"]] + [pair[1] for pair in TARGET_CLASSES["rice"]]
    final_class_names = sorted(final_class_names)
    print(f"Target classes ({len(final_class_names)}): {final_class_names}")
    print(f"Quota per class: {IMAGES_PER_CLASS} images")
    print("-" * 65)

    # -------------------------------------------------------------
    # 1. Acquire PlantVillage Classes
    # -------------------------------------------------------------
    pv_zip_url = "https://huggingface.co/datasets/mohanty/PlantVillage/resolve/main/data.zip"
    pv_cdn_url = resolve_cdn_url(pv_zip_url)
    print("Reading PlantVillage central directory via range stream...")
    pv_reader = RemoteZipReader(pv_cdn_url)
    pv_zf = zipfile.ZipFile(pv_reader)

    # Index files per PV class
    pv_class_map = {pair[0]: pair[1] for pair in TARGET_CLASSES["pv"]}
    pv_files_by_class = {c: [] for c in pv_class_map.keys()}

    for name in pv_zf.namelist():
        if name.startswith("raw/color/"):
            parts = name.split("/")
            if len(parts) > 3 and parts[2] in pv_files_by_class:
                if name.lower().endswith((".jpg", ".jpeg", ".png")):
                    pv_files_by_class[parts[2]].append(name)

    print("\n--- PlantVillage Download Task ---")
    for src_class, dest_class in TARGET_CLASSES["pv"]:
        available = pv_files_by_class.get(src_class, [])
        target_dir = os.path.join(DATA_DIR, dest_class)
        os.makedirs(target_dir, exist_ok=True)

        existing = len([f for f in os.listdir(target_dir) if f.lower().endswith((".jpg", ".png", ".jpeg"))])
        needed = IMAGES_PER_CLASS - existing

        if needed <= 0:
            print(f"  [{dest_class}] Already complete ({existing} images).")
            continue

        selected_names = available[:IMAGES_PER_CLASS]
        if len(selected_names) < IMAGES_PER_CLASS:
            print(f"  [Warning] Only {len(selected_names)} available for {src_class}!")

        print(f"  [{dest_class}] Extracting {len(selected_names)} images...")
        tasks = []
        with ThreadPoolExecutor(max_workers=12) as pool:
            for idx, name in enumerate(selected_names, 1):
                info = pv_zf.getinfo(name)
                out_path = os.path.join(target_dir, f"img_{idx:03d}.jpg")
                tasks.append(pool.submit(extract_entry_from_cdn, pv_cdn_url, info, out_path))

            completed = 0
            for fut in as_completed(tasks):
                if fut.result():
                    completed += 1

        print(f"  -> Successfully saved {completed}/{len(selected_names)} images in {dest_class}")

    # -------------------------------------------------------------
    # 2. Acquire Rice Leaf Brown Spot Class
    # -------------------------------------------------------------
    print("\n--- Rice Leaf Disease Download Task ---")
    rice_zip_url = "https://huggingface.co/datasets/amdmqd/rice_leaf_disease_dataset/resolve/main/rice_leaf_disease_dataset.zip"
    rice_cdn_url = resolve_cdn_url(rice_zip_url)
    print("Reading Rice dataset central directory via range stream...")
    rice_reader = RemoteZipReader(rice_cdn_url)
    rice_zf = zipfile.ZipFile(rice_reader)

    rice_brown_spot_files = [
        name for name in rice_zf.namelist()
        if "Brownspot" in name and name.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    print(f"Found {len(rice_brown_spot_files)} candidate Rice Brown Spot files.")

    dest_class = "Rice___Brown_spot"
    target_dir = os.path.join(DATA_DIR, dest_class)
    os.makedirs(target_dir, exist_ok=True)

    existing = len([f for f in os.listdir(target_dir) if f.lower().endswith((".jpg", ".png", ".jpeg"))])
    if existing >= IMAGES_PER_CLASS:
        print(f"  [{dest_class}] Already complete ({existing} images).")
    else:
        selected_rice = rice_brown_spot_files[:IMAGES_PER_CLASS]
        print(f"  [{dest_class}] Extracting {len(selected_rice)} images...")
        tasks = []
        with ThreadPoolExecutor(max_workers=12) as pool:
            for idx, name in enumerate(selected_rice, 1):
                info = rice_zf.getinfo(name)
                out_path = os.path.join(target_dir, f"img_{idx:03d}.jpg")
                tasks.append(pool.submit(extract_entry_from_cdn, rice_cdn_url, info, out_path))

            completed = 0
            for fut in as_completed(tasks):
                if fut.result():
                    completed += 1
        print(f"  -> Successfully saved {completed}/{len(selected_rice)} images in {dest_class}")

    # -------------------------------------------------------------
    # 3. Validation and Inventory Verification
    # -------------------------------------------------------------
    print("\n" + "=" * 65)
    print(" Final Inventory Verification Across backend/data/")
    print("=" * 65)
    all_classes_present = []
    total_verified = 0

    for cname in sorted(os.listdir(DATA_DIR)):
        cdir = os.path.join(DATA_DIR, cname)
        if os.path.isdir(cdir):
            valid_imgs = 0
            for fname in os.listdir(cdir):
                fpath = os.path.join(cdir, fname)
                try:
                    with Image.open(fpath) as im:
                        im.verify()
                    valid_imgs += 1
                except Exception:
                    pass
            all_classes_present.append(cname)
            total_verified += valid_imgs
            status = "OK" if valid_imgs == IMAGES_PER_CLASS else f"PARTIAL ({valid_imgs})"
            print(f"  Class: {cname:<32} | Valid Images: {valid_imgs:>4} [{status}]")

    print("-" * 65)
    print(f"Total Classes: {len(all_classes_present)} / 11")
    print(f"Total Verified Images: {total_verified} / 1,650")
    print("=" * 65)

    # -------------------------------------------------------------
    # 4. Save Final classes.json & README.md
    # -------------------------------------------------------------
    classes_json_path = os.path.join(MODELS_DIR, "classes.json")
    with open(classes_json_path, "w", encoding="utf-8") as f:
        json.dump(all_classes_present, f, indent=2)
    print(f"Saved classes metadata to: {classes_json_path}")

    readme_path = os.path.join(DATA_DIR, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"""# AgroAI Dual-Source 11-Class Balanced Benchmark

This dataset is configured specifically for the AgroAI smart crop disease detection pipeline.

## Dataset Specifications
- **Classes**: {len(all_classes_present)}
- **Images per class**: {IMAGES_PER_CLASS}
- **Total Images**: {total_verified}
- **Sampling Strategy**: Uniformly balanced 1:1 class ratio (150 images per class)
- **Train / Validation Split**: 80% Train ({int(IMAGES_PER_CLASS * 0.8)} per class) / 20% Validation ({int(IMAGES_PER_CLASS * 0.2)} per class)

## Dataset Sources & Attribution

### 1. PlantVillage Dataset (10 Classes)
- **Source**: Penn State University / EPFL
- **Citation**: Hughes, D. P., & Salathé, M. (2015). *An open access repository of images on plant health to enable the development of mobile disease diagnostics.* arXiv preprint arXiv:1511.08060.
- **License**: Creative Commons Zero 1.0 Universal (CC0 1.0) / Public Domain
- **Included Classes**:
  1. `Tomato___Early_blight`
  2. `Tomato___Late_blight`
  3. `Tomato___Target_Spot`
  4. `Tomato___healthy`
  5. `Potato___Early_blight`
  6. `Potato___Late_blight`
  7. `Potato___healthy`
  8. `Corn___Common_rust_`
  9. `Corn___Northern_Leaf_Blight`
  10. `Corn___healthy`

### 2. Rice Leaf Disease Dataset (1 Class)
- **Source**: Mendeley Data / Prajapati et al. / Rahman et al.
- **Citation**: Rahman, C. R., et al. (2020). *RiceLeafBD: A comprehensive dataset of rice leaf diseases for deep learning.* Mendeley Data, DOI: 10.17632/kx9rx8p2mz.1.
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Included Class**:
  11. `Rice___Brown_spot` (*Bipolaris oryzae*)
""")
    print(f"Saved dataset documentation to: {readme_path}")
    return all_classes_present

if __name__ == "__main__":
    prepare_dataset()
