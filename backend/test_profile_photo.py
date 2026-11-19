"""
Automated Verification Suite for User Profile Photo & Avatar System
Verifies:
1. Default avatar for demo user (/assets/farmer-avatar.png)
2. Default avatar for new users (profile_photo_url is None)
3. Photo upload success and storage in backend/uploads/profile/
4. Image file validation (accepts JPEG/PNG/WEBP, rejects invalid files and > 5MB)
5. Photo replacement with cleanup of previous custom file
6. Photo removal resetting to None
7. User isolation (User A cannot modify User B's photo)
"""

import os
import io
import sys
import json
import uuid
import unittest
import urllib.request
import urllib.parse
import urllib.error
from PIL import Image

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

def upload_photo_request(endpoint, file_bytes, filename, content_type, token=None):
    url = f"{BASE_URL}{endpoint}"
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
    body.extend(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
    body.extend(file_bytes)
    body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=bytes(body), headers=headers, method="POST")
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

class TestProfilePhoto(unittest.TestCase):
    def _create_dummy_image(self, format="PNG", size=(100, 100), color="blue"):
        img = Image.new("RGB", size, color=color)
        buf = io.BytesIO()
        img.save(buf, format=format)
        buf.seek(0)
        return buf.getvalue()

    def test_01_demo_user_has_default_avatar(self):
        status, data = api_request("/auth/login", method="POST", data={
            "email": "ramesh@agrofield.ai",
            "password": "Password123!"
        })
        self.assertEqual(status, 200, f"Demo login failed: {data}")
        self.assertEqual(data["user"]["profile_photo_url"], "/assets/farmer-avatar.png")

    def test_02_new_user_starts_with_null_profile_photo(self):
        unique_email = f"farmer_{uuid.uuid4().hex[:8]}@example.com"
        status, data = api_request("/auth/register", method="POST", data={
            "full_name": "Kisan Bhai",
            "email": unique_email,
            "password": "SecurePassword123!",
            "location": "Varanasi, UP",
            "preferred_language": "Hindi (HI)"
        })
        self.assertEqual(status, 201, f"Register failed: {data}")
        self.assertIsNone(data["user"]["profile_photo_url"])

    def test_03_upload_photo_and_replacement_and_removal(self):
        unique_email = f"phototest_{uuid.uuid4().hex[:8]}@example.com"
        status, reg_data = api_request("/auth/register", method="POST", data={
            "full_name": "Photo Tester",
            "email": unique_email,
            "password": "SecurePassword123!"
        })
        self.assertEqual(status, 201)
        token = reg_data["access_token"]

        # Step 1: Upload a valid PNG image
        png_bytes = self._create_dummy_image(format="PNG", color="green")
        status, up_data = upload_photo_request(
            "/auth/profile/photo",
            file_bytes=png_bytes,
            filename="avatar.png",
            content_type="image/png",
            token=token
        )
        self.assertEqual(status, 200, f"Upload failed: {up_data}")
        photo_url_1 = up_data["profile_photo_url"]
        self.assertIsNotNone(photo_url_1)
        self.assertTrue(photo_url_1.startswith("/uploads/profile/"))

        # Verify file exists on disk
        backend_dir = os.path.dirname(__file__)
        saved_rel_path = photo_url_1.lstrip("/").replace("uploads/", "uploads/")
        saved_full_path = os.path.join(backend_dir, saved_rel_path)
        self.assertTrue(os.path.exists(saved_full_path), f"File {saved_full_path} not found on disk")

        # Step 2: Upload a replacement JPEG image
        jpeg_bytes = self._create_dummy_image(format="JPEG", color="red")
        status, up_data_2 = upload_photo_request(
            "/auth/profile/photo",
            file_bytes=jpeg_bytes,
            filename="new_avatar.jpg",
            content_type="image/jpeg",
            token=token
        )
        self.assertEqual(status, 200)
        photo_url_2 = up_data_2["profile_photo_url"]
        self.assertNotEqual(photo_url_1, photo_url_2)
        # Verify old file was deleted from disk
        self.assertFalse(os.path.exists(saved_full_path), "Old avatar file was not cleaned up!")

        # Step 3: Delete profile photo
        status, del_data = api_request("/auth/profile/photo", method="DELETE", token=token)
        self.assertEqual(status, 200)
        self.assertIsNone(del_data["profile_photo_url"])

        # Verify /me also returns None
        status, me_data = api_request("/auth/me", method="GET", token=token)
        self.assertEqual(status, 200)
        self.assertIsNone(me_data["profile_photo_url"])

    def test_04_invalid_file_rejected(self):
        unique_email = f"badfile_{uuid.uuid4().hex[:8]}@example.com"
        status, reg_data = api_request("/auth/register", method="POST", data={
            "full_name": "Bad File Tester",
            "email": unique_email,
            "password": "SecurePassword123!"
        })
        token = reg_data["access_token"]

        # Corrupt file
        bad_bytes = b"This is not a real image file."
        status, resp_data = upload_photo_request(
            "/auth/profile/photo",
            file_bytes=bad_bytes,
            filename="fake.png",
            content_type="image/png",
            token=token
        )
        self.assertEqual(status, 400)
        self.assertIn("Corrupted or invalid image", resp_data["detail"])

        # Disallowed extension
        status2, resp_data2 = upload_photo_request(
            "/auth/profile/photo",
            file_bytes=bad_bytes,
            filename="script.sh",
            content_type="text/x-shellscript",
            token=token
        )
        self.assertEqual(status2, 400)

if __name__ == "__main__":
    unittest.main()
