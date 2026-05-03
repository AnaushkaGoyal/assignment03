"""
    Script to transform raw AirNow data files into BigQuery-compatible formats.

    This script reads the raw .dat files downloaded by 01_extract.py and
    converts them into CSV, JSON-L, and Parquet formats suitable
    for loading into BigQuery as external tables.

    Hourly observation data is converted to: CSV, JSON-L, Parquet
    Site location data is converted to: CSV, JSON-L, GeoParquet
    (with point geometry)

    Usage:
        python scripts/02_prepare.py
"""

import pathlib
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

DATA_DIR = pathlib.Path(__file__).parent.parent / 'data'

HOURLY_COLUMNS = [
    'valid_date',
    'valid_time',
    'aqsid',
    'site_name',
    'gmt_offset',
    'parameter_name',
    'reporting_units',
    'value',
    'data_source',
]

SITE_COLUMNS = [
    'StationID', 'AQSID', 'FullAQSID', 'Parameter', 'MonitorType',
    'SiteCode', 'SiteName', 'Status', 'AgencyID', 'AgencyName',
    'EPARegion', 'Latitude', 'Longitude', 'Elevation', 'GMTOffset',
    'CountryFIPS', 'CBSA_ID', 'CBSA_Name', 'StateAQSCode',
    'StateAbbreviation', 'CountyAQSCode', 'CountyName',
]


def _read_hourly(date_str):
    """Read all 24 hourly .dat files for a date into a single DataFrame."""
    raw_dir = DATA_DIR / 'raw' / date_str
    dfs = []
    for f in sorted(raw_dir.glob('HourlyData_*.dat')):
        df = pd.read_csv(f, sep='|', header=None, names=HOURLY_COLUMNS,
                         encoding='latin-1', low_memory=False)
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def _read_sites():
    """Read the most recent site locations file into a DataFrame."""
    raw_dirs = sorted((DATA_DIR / 'raw').iterdir())
    site_file = raw_dirs[-1] / 'Monitoring_Site_Locations_V2.dat'
    df = pd.read_csv(site_file, sep='|', header=0, encoding='latin-1',
                     low_memory=False)
    # One row per site, not per site-parameter
    df = df.drop_duplicates(subset='StationID').reset_index(drop=True)
    return df


# --- Hourly observation data ---

def prepare_hourly_csv(date_str):
    out_dir = DATA_DIR / 'prepared' / 'hourly'
    out_dir.mkdir(parents=True, exist_ok=True)
    df = _read_hourly(date_str)
    df.to_csv(out_dir / f'{date_str}.csv', index=False)


def prepare_hourly_jsonl(date_str):
    out_dir = DATA_DIR / 'prepared' / 'hourly'
    out_dir.mkdir(parents=True, exist_ok=True)
    df = _read_hourly(date_str)
    df.to_json(out_dir / f'{date_str}.jsonl', orient='records', lines=True)


def prepare_hourly_parquet(date_str):
    out_dir = DATA_DIR / 'prepared' / 'hourly'
    out_dir.mkdir(parents=True, exist_ok=True)
    df = _read_hourly(date_str)
    df.to_parquet(out_dir / f'{date_str}.parquet', index=False)


# --- Site location data ---

def prepare_site_locations_csv():
    out_dir = DATA_DIR / 'prepared' / 'sites'
    out_dir.mkdir(parents=True, exist_ok=True)
    df = _read_sites()
    df.to_csv(out_dir / 'site_locations.csv', index=False)


def prepare_site_locations_jsonl():
    out_dir = DATA_DIR / 'prepared' / 'sites'
    out_dir.mkdir(parents=True, exist_ok=True)
    df = _read_sites()
    df.to_json(out_dir / 'site_locations.jsonl', orient='records', lines=True)


def prepare_site_locations_geoparquet():
    out_dir = DATA_DIR / 'prepared' / 'sites'
    out_dir.mkdir(parents=True, exist_ok=True)
    df = _read_sites()
    geometry = [
        Point(lon, lat) if pd.notna(lon) and pd.notna(lat) else None
        for lat, lon in zip(df['Latitude'], df['Longitude'])
    ]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
    gdf.to_parquet(out_dir / 'site_locations.geoparquet', index=False)


if __name__ == '__main__':
    import datetime

    print('Preparing site locations...')
    prepare_site_locations_csv()
    prepare_site_locations_jsonl()
    prepare_site_locations_geoparquet()

    start_date = datetime.date(2024, 7, 1)
    end_date = datetime.date(2024, 7, 31)
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()
        print(f'Preparing hourly data for {date_str}...')
        prepare_hourly_csv(date_str)
        prepare_hourly_jsonl(date_str)
        prepare_hourly_parquet(date_str)
        current_date += datetime.timedelta(days=1)

    print('Done.')
