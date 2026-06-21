# AWS S3 Automated Backup Tool

A lightweight Python utility to automate directory backups to an Amazon S3 bucket. This script is designed to run as a cron job or scheduled task to ensure local data is regularly archived.

## Features
- Recursive directory scanning
- Dynamic S3 bucket destination routing
- Standard AWS credential profile support

## Prerequisites
- Python 3.8 or higher
- `boto3` library
- Configured AWS CLI credentials

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/aws-s3-backup-tool.git
   cd aws-s3-backup-tool
