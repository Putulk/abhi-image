import os
import csv
import requests
import json
import base64
import subprocess
from datetime import datetime, timezone
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo
# ==========================
# CONFIGURATION
# ==========================
CSV_FILE_PATH="/tmp/abhi_img_2.csv"
# CSV_FILE_PATH = "/tmp/sample_1.csv"
SECRET_KEY = ""
AUTH_TOKEN = ""
API_URL = "https://arog.abhicl.in/ABHICL_Embedded_Wellness/enc/CTcreateVideo"

# ==========================
# AES ENCRYPTION FUNCTION
# ==========================
def normalize_key(secret_key: str) -> bytes:
    key_bytes = secret_key.encode("utf-8")
    if len(key_bytes) < 16:
        key_bytes = key_bytes.ljust(16, b"\0")
    elif len(key_bytes) > 32:
        key_bytes = key_bytes[:32]
    elif len(key_bytes) not in (16, 24, 32):
        key_bytes = key_bytes.ljust(32, b"\0")
    return key_bytes


def encrypt_with_random_iv(plain_text: str, secret_key: str) -> str:
    key_bytes = normalize_key(secret_key)
    iv = get_random_bytes(16)
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    padded_data = pad(plain_text.encode("utf-8"), AES.block_size)
    encrypted_bytes = cipher.encrypt(padded_data)

    iv_base64 = base64.b64encode(iv).decode("utf-8")
    encrypted_base64 = base64.b64encode(encrypted_bytes).decode("utf-8")

    return f"{iv_base64}.{encrypted_base64}"


def send_api_request(encrypted_payload: str):
    """Send encrypted payload using Python requests"""
    headers = {
        "Authorization": AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {"EncryptedPayload": encrypted_payload}

    print(" Sending API request...")
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        print(f"Response Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def main():
    if not os.path.exists(CSV_FILE_PATH):
        print(f"CSV file not found: {CSV_FILE_PATH}")
        return

    with open(CSV_FILE_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        # Strip whitespace from header names
        reader.fieldnames = [name.strip() for name in reader.fieldnames]

        row_count = 0
        success_count = 0
        failed_count = 0
        current_time_ist = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()

        for row in reader:
            row_count += 1

            # Strip whitespace from all values
            row = {k.strip(): (v.strip() if v else v) for k, v in row.items()}

            media_url = row.get("MediaUrl")
            member_code = row.get("PARTY_CODE")

            print(f"\nRow {row_count}:")
            print(f" MediaUrl: '{media_url[:50]}...' " if media_url else f"   MediaUrl: None")

            if not media_url:
                print(f" SKIPPING - Missing data")
                failed_count += 1
                continue

            # Prepare event JSON
            event_json = {
                "d": [
                    {
                        "identity": member_code,
                        "evtName": "ai_video_create",
                        "evtData": {
                            "templateName": "pb_app_install_img_2",
                            "Member_Code": member_code,

                            "video_url": media_url,
                            "eventDate": datetime.now(timezone.utc).isoformat()
                        },
                        "type": "event"
                    }
                ]
            }

            json_str = json.dumps(event_json, separators=(",", ":"))

            encrypted_payload = encrypt_with_random_iv(json_str, SECRET_KEY)
            log_path = f"/tmp/abhi_image_{current_time_ist}.log"
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"\nRow {row_count}:\n")
                log_file.write(f"Member Code: {member_code}\n")
                log_file.write(f"Event DateTime: {datetime.now(timezone.utc).isoformat()}\n")
                log_file.write(f"Encrypted Payload:\n{encrypted_payload}\n")
                log_file.write("=" * 80 + "\n")

            print(f"Log file saved at: {log_path}")

            response = send_api_request(encrypted_payload)

            if response and response.status_code == 200:
                success_count += 1
            else:
                failed_count += 1

        print("\n" + "=" * 80)
        print(f"Summary:")
        print(f"  Total rows: {row_count}")
        print(f"  Successful: {success_count}")
        print(f"  Failed: {failed_count}")


if __name__ == "__main__":
    main()