"""
    Stretch challenge: Prepare merged hourly + site location data.
"""

import pathlib
import datetime
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

DATA_DIR = pathlib.Path(__file__).parent.parent / 'data'

HOURLY_COLUMNS = [
    'valid_date', 'valid_time', 'aqsid', 'site_name', 'gmt_offset',
    'parameter_name', 'reporting_units', 'value', 'data_source',
]


def _read_hourly(date_str):
    raw_dir = DATA_DIR / 'raw' / date_str
    dfs = []
    for f in sorted(raw_dir.glob('HourlyData_*.dat')):
        df = pd.read_csv(f, sep='|', header=None, names=HOURLY_COLUMNS,
                         encoding='latin-1', low_memory=False)
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def _read_sites():
    raw_dirs = sorted((DATA_DIR / 'raw').iterdir())
    site_file = raw_dirs[-1] / 'Monitoring_Site_Locations_V2.dat'
    df = pd.read_csv(site_file, sep='|', header=0, encoding='latin-1',
                     low_memory=False)
    return df.drop_duplicates(subset='StationID').reset_index(drop=True)


def _merge(date_str):
    hourly = _read_hourly(date_str)
    sites = _read_sites()
    sites_slim = sites[[
        'AQSID', 'Latitude', 'Longitude', 'Elevation', 'GMTOffset',
        'StateAbbreviation', 'CountyName', 'CBSA_Name', 'AgencyName',
        'CountryFIPS',
    ]]
    merged = hourly.merge(sites_slim, left_on='aqsid', right_on='AQSID',
                          how='left')
    merged.drop(columns=['AQSID'], inplace=True)
    return merged


def prepare_merged_csv(date_str):
    out_dir = DATA_DIR / 'prepared' / 'hourly_with_sites'
    out_dir.mkdir(parents=True, exist_ok=True)
    _merge(date_str).to_csv(out_dir / f'{date_str}.csv', index=False)


def prepare_merged_jsonl(date_str):
    out_dir = DATA_DIR / 'prepared' / 'hourly_with_sites'
    out_dir.mkdir(parents=True, exist_ok=True)
    _merge(date_str).to_json(out_dir / f'{date_str}.jsonl',
                             orient='records', lines=True)


def prepare_merged_geoparquet(date_str):
    out_dir = DATA_DIR / 'prepared' / 'hourly_with_sites'
    out_dir.mkdir(parents=True, exist_ok=True)
    df = _merge(date_str)
    geometry = [
        Point(lon, lat)
        if pd.notna(lon) and pd.notna(lat) else None
        for lat, lon in zip(df['Latitude'], df['Longitude'])
    ]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
    gdf.to_parquet(out_dir / f'{date_str}.geoparquet', index=False)


if __name__ == '__main__':
    start_date = datetime.date(2024, 7, 1)
    end_date = datetime.date(2024, 7, 31)
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()
        print(f'Preparing merged data for {date_str}...')
        prepare_merged_csv(date_str)
        prepare_merged_jsonl(date_str)
        prepare_merged_geoparquet(date_str)
        current_date += datetime.timedelta(days=1)
    print('Done.')
