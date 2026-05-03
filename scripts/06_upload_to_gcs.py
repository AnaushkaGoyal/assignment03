"""
    Stretch challenge: Upload merged hourly + site location data to GCS.
"""

import pathlib
from google.cloud import storage

DATA_DIR = pathlib.Path(__file__).parent.parent / 'data'
BUCKET_NAME = 'musa5090-s26-goyal-data'
PROJECT_ID = 'musa-cloudcomputing-spring2026'
PREPARED_MERGED = DATA_DIR / 'prepared' / 'hourly_with_sites'


def upload_merged_data():
    client = storage.Client(project=PROJECT_ID)
    bucket = client.get_bucket(BUCKET_NAME)

    for local_path in sorted(PREPARED_MERGED.iterdir()):
        if not local_path.is_file():
            continue

        date_str = local_path.stem
        ext = local_path.suffix.lstrip('.')

        blob_name = (
            f'air_quality/hourly_with_sites/{ext}/'
            f'airnow_date={date_str}/data.{ext}'
        )
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(str(local_path))
        print(f'  Uploaded {blob_name}')


if __name__ == '__main__':
    upload_merged_data()
    print('Done.')
