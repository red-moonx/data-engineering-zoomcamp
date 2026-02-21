import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage
from google.api_core.exceptions import NotFound, Forbidden
import time


# ── Configuration ──────────────────────────────────────────────────────────────
BUCKET_NAME = "dezoomcamp_hw4_lunazea_2026"
CREDENTIALS_FILE = "de-zoomcamp-module4-luna-65a6fedc7780.json"

client = storage.Client.from_service_account_json(CREDENTIALS_FILE)

# DataTalksClub GitHub releases base URL
# Files are hosted as: .../download/<color>/<color>_tripdata_<year>-<month>.csv.gz
BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download"

COLORS = ["yellow", "green"]
YEARS = [2019, 2020]
MONTHS = [f"{i:02d}" for i in range(1, 13)]

DOWNLOAD_DIR = "."
CHUNK_SIZE = 8 * 1024 * 1024

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

bucket = client.bucket(BUCKET_NAME)


def download_file(color, year, month):
    filename = f"{color}_tripdata_{year}-{month}.csv.gz"
    url = f"{BASE_URL}/{color}/{filename}"
    file_path = os.path.join(DOWNLOAD_DIR, filename)

    try:
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, file_path)
        print(f"Downloaded: {file_path}")
        return file_path
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None


def create_bucket(bucket_name):
    try:
        client.get_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' exists and is accessible. Proceeding...")

    except NotFound:
        client.create_bucket(bucket_name)
        print(f"Created bucket '{bucket_name}'")
    except Forbidden:
        print(
            f"Bucket '{bucket_name}' exists but is not accessible. "
            "Check that the service account has the required permissions."
        )
        sys.exit(1)


def verify_gcs_upload(blob_name):
    return storage.Blob(bucket=bucket, name=blob_name).exists(client)


def upload_to_gcs(file_path, max_retries=3):
    if file_path is None:
        return

    blob_name = os.path.basename(file_path)
    blob = bucket.blob(blob_name)
    blob.chunk_size = CHUNK_SIZE

    for attempt in range(max_retries):
        try:
            print(f"Uploading {file_path} to {BUCKET_NAME} (Attempt {attempt + 1})...")
            blob.upload_from_filename(file_path)
            print(f"Uploaded: gs://{BUCKET_NAME}/{blob_name}")

            if verify_gcs_upload(blob_name):
                print(f"Verification successful: {blob_name}")
                os.remove(file_path)  # Clean up local file after successful upload
                return
            else:
                print(f"Verification failed for {blob_name}, retrying...")
        except Exception as e:
            print(f"Failed to upload {file_path}: {e}")

        time.sleep(5)

    print(f"Giving up on {file_path} after {max_retries} attempts.")


def process_color_year(color, year):
    print(f"\n{'='*50}")
    print(f"Processing {color} taxi data for {year}")
    print(f"{'='*50}")

    # Download all months in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(download_file, color, year, month): month
            for month in MONTHS
        }
        file_paths = [f.result() for f in futures]

    # Upload all downloaded files in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(upload_to_gcs, filter(None, file_paths))


if __name__ == "__main__":
    create_bucket(BUCKET_NAME)

    for color in COLORS:
        for year in YEARS:
            process_color_year(color, year)

    print("\nAll files processed and verified.")
