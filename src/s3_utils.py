import boto3
import os
import zipfile

def download_file(bucket, key, local_path):
    """Download file from S3 only if not already present."""
    if not os.path.exists(local_path):
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        s3 = boto3.client("s3")
        print(f"[S3] Downloading {key}...")
        s3.download_file(bucket, key, local_path)
        print("[S3] Done.")

def download_and_extract_zip(bucket, key, extract_to):
    """Download zip from S3 and extract if not already present."""

    # If FAISS folder already exists → skip
    faiss_folder = os.path.join(extract_to, "faiss_index")
    if os.path.exists(faiss_folder):
        return

    zip_path = "temp_faiss.zip"

    s3 = boto3.client("s3")
    print(f"[S3] Downloading {key}...")
    s3.download_file(bucket, key, zip_path)

    print("[S3] Extracting...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    os.remove(zip_path)
    print("[S3] Done.")