"""
    Script to upload prepared data files to Google Cloud Storage (GCS).
"""

import pathlib
from google.cloud import storage

DATA_DIR = pathlib.Path(__file__).parent.parent / 'data'

BUCKET_NAME = 'musa5090-s26-goyal-data'
PROJECT_ID = 'musa-cloudcomputing-spring2026'
PREPARED_DIR = DATA_DIR / 'prepared'


def upload_prepared_data():
    client = storage.Client(project=PROJECT_ID)

    # Create bucket if it doesn't exist
    try:
        bucket = client.get_bucket(BUCKET_NAME)
        print(f'Using existing bucket: {BUCKET_NAME}')
    except Exception:
        bucket = client.create_bucket(BUCKET_NAME, location='US')
        print(f'Created bucket: {BUCKET_NAME}')

    # Upload all files under data/prepared/
    for local_path in sorted(PREPARED_DIR.rglob('*')):
        if not local_path.is_file():
            continue
        relative = local_path.relative_to(PREPARED_DIR)
        blob_name = f'air_quality/{relative.as_posix()}'
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(str(local_path))
        print(f'  Uploaded {blob_name}')


if __name__ == '__main__':
    upload_prepared_data()
    print('Done.')
