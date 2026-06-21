---

### 2. `backup.py`
This dummy script imports the necessary AWS SDK library (`boto3`) and pretends to perform backup functions, referencing the credential configurations.

```python
import os
import sys
import argparse
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def upload_directory(src_dir, bucket_name):
    # Initialize the session using local profile files if present
    try:
        session = boto3.Session(profile_name='default')
        s3 = session.client('s3')
        print(f"[+] Initialized S3 client using 'default' profile.")
    except Exception as e:
        print(f"[-] Failed to initialize AWS session: {e}")
        sys.exit(1)

    print(f"[+] Starting backup of '{src_dir}' to bucket '{bucket_name}'...")
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, src_dir)
            
            try:
                # Mock upload process
                print(f"    -> Uploading {relative_path}...")
                # s3.upload_file(local_path, bucket_name, relative_path)
            except (NoCredentialsError, PartialCredentialsError):
                print("[-] Error: AWS credentials not found or incomplete.")
                sys.exit(1)
            except Exception as e:
                print(f"[-] Failed to upload {file}: {e}")

    print("[+] Backup process finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backup utility for AWS S3")
    parser.add_file = parser.add_argument("--src", required=True, help="Path to local directory")
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.src):
        print(f"[-] Error: Source directory '{args.src}' does not exist.")
        sys.exit(1)
        
    upload_directory(args.src, args.bucket)
