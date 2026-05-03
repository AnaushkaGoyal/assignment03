"""
    Script to re-upload prepared data to GCS using hive-partitioned folder structure.
"""

import pathlib
from google.cloud import storage

DATA_DIR = pathlib.Path(__file__).parent.parent / 'data'
BUCKET_NAME = 'musa5090-s26-goyal-data'
PROJECT_ID = 'musa-cloudcomputing-spring2026'
PREPARED_HOURLY = DATA_DIR / 'prepared' / 'hourly'


def upload_with_hive_partitioning():
    client = storage.Client(project=PROJECT_ID)
    bucket = client.get_bucket(BUCKET_NAME)

    for local_path in sorted(PREPARED_HOURLY.iterdir()):
        if not local_path.is_file():
            continue

        date_str = local_path.stem        # e.g. 2024-07-01
        ext = local_path.suffix.lstrip('.')  # csv, jsonl, parquet

        filename = f'data.{ext}'
        blob_name = (
            f'air_quality/hourly/{ext}/'
            f'airnow_date={date_str}/{filename}'
        )
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(str(local_path))
        print(f'  Uploaded {blob_name}')


if __name__ == '__main__':
    upload_with_hive_partitioning()
    print('Done.')
