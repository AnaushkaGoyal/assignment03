import pathlib
import urllib.request

DATA_DIR = pathlib.Path(__file__).parent.parent / 'data'

BASE_URL = "https://files.airnowtech.org/airnow"


def download_data_for_date(date_str):
    year, month, day = date_str.split('-')
    date_compact = f"{year}{month}{day}"
    out_dir = DATA_DIR / 'raw' / date_str
    out_dir.mkdir(parents=True, exist_ok=True)
    date_url = f"{BASE_URL}/{year}/{date_compact}"

    for hour in range(24):
        hour_str = str(hour).zfill(2)
        filename = f"HourlyData_{date_compact}{hour_str}.dat"
        url = f"{date_url}/{filename}"
        dest = out_dir / filename
        if dest.exists():
            print(f"  Skipping {filename} (already exists)")
            continue
        try:
            urllib.request.urlretrieve(url, dest)
            print(f"  Downloaded {filename}")
        except Exception as e:
            print(f"  Failed to download {filename}: {e}")

    site_filename = "Monitoring_Site_Locations_V2.dat"
    site_url = f"{date_url}/{site_filename}"
    site_dest = out_dir / site_filename
    if site_dest.exists():
        print(f"  Skipping {site_filename} (already exists)")
    else:
        try:
            urllib.request.urlretrieve(site_url, site_dest)
            print(f"  Downloaded {site_filename}")
        except Exception as e:
            print(f"  Failed to download {site_filename}: {e}")


if __name__ == '__main__':
    import datetime
    start_date = datetime.date(2024, 7, 1)
    end_date = datetime.date(2024, 7, 31)
    current_date = start_date
    while current_date <= end_date:
        print(f'Downloading data for {current_date}...')
        download_data_for_date(current_date.isoformat())
        current_date += datetime.timedelta(days=1)
    print('Done.')
