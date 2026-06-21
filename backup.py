#!/usr/bin/env python3
"""backup.py - Upload a local directory to an S3 bucket.

Improvements over the original:
- Fixed argparse usage bug
- Uses logging instead of print()
- Optional AWS profile and dry-run mode
- Proper error handling for boto3/botocore exceptions
- Normalizes S3 object keys to use '/' separators
- Reports summary of uploaded files
"""

import os
import sys
import argparse
import logging
from typing import Optional

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def upload_directory(src_dir: str, bucket_name: str, profile_name: Optional[str] = None, dry_run: bool = False) -> int:
    """Upload all files under src_dir to the specified S3 bucket.

    Returns the number of files successfully uploaded.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_credentials = os.path.join(script_dir, ".aws", "credentials")

        if profile_name:
            session = boto3.Session(profile_name=profile_name)
            logger.info("Initialized S3 client using profile '%s'.", profile_name)
        else:
            if not os.environ.get("AWS_SHARED_CREDENTIALS_FILE") and os.path.isfile(local_credentials):
                os.environ["AWS_SHARED_CREDENTIALS_FILE"] = local_credentials
                logger.info("Using local AWS credentials file: %s", local_credentials)
            session = boto3.Session()
            logger.info("Initialized S3 client using AWS credential chain.")

        s3 = session.client("s3")
    except (NoCredentialsError, PartialCredentialsError) as e:
        logger.error("AWS credentials not found or incomplete: %s", e)
        raise
    except Exception as e:
        logger.error("Failed to initialize AWS session: %s", e)
        raise

    logger.info("Starting backup of '%s' to bucket '%s'%s", src_dir, bucket_name, " (dry-run)" if dry_run else "")

    uploaded = 0
    for root, _, files in os.walk(src_dir):
        for file in files:
            local_path = os.path.join(root, file)
            # Use forward slashes for S3 keys regardless of OS
            relative_path = os.path.relpath(local_path, src_dir)
            s3_key = relative_path.replace(os.path.sep, "/")

            if dry_run:
                logger.info("[dry-run] -> %s", s3_key)
                uploaded += 1
                continue

            try:
                logger.debug("Uploading %s -> s3://%s/%s", local_path, bucket_name, s3_key)
                s3.upload_file(local_path, bucket_name, s3_key)
                uploaded += 1
                logger.info("Uploaded: %s", s3_key)
            except (NoCredentialsError, PartialCredentialsError):
                logger.error("AWS credentials not found or incomplete while uploading %s", s3_key)
                raise
            except ClientError as e:
                logger.error("Failed to upload %s: %s", s3_key, e)
            except FileNotFoundError:
                logger.warning("File not found, skipping: %s", local_path)
            except Exception as e:
                logger.error("Unexpected error uploading %s: %s", s3_key, e)

    logger.info("Backup process finished. Total files processed (or simulated): %d", uploaded)
    return uploaded


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backup a local directory to an AWS S3 bucket")
    parser.add_argument("--src", required=True, help="Path to local directory")
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    parser.add_argument("--profile", default=None, help="AWS profile name (optional)")
    parser.add_argument("--dry-run", action="store_true", help="Do not perform uploads; just show what would be done")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if not os.path.isdir(args.src):
        logger.error("Source directory '%s' does not exist.", args.src)
        return 2

    try:
        _ = upload_directory(args.src, args.bucket, profile_name=args.profile, dry_run=args.dry_run)
    except (NoCredentialsError, PartialCredentialsError):
        logger.error("Aborting due to AWS credential error.")
        return 3
    except Exception as e:
        logger.error("Aborting due to unexpected error: %s", e)
        return 4

    return 0


if __name__ == "__main__":
    sys.exit(main())
