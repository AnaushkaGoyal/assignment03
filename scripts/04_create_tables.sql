-- Part 4: Create BigQuery external tables

-- Hourly Observations — CSV
CREATE OR REPLACE EXTERNAL TABLE `musa-cloudcomputing-spring2026.air_quality.hourly_observations_csv`
(
    valid_date STRING,
    valid_time STRING,
    aqsid STRING,
    site_name STRING,
    gmt_offset FLOAT64,
    parameter_name STRING,
    reporting_units STRING,
    value FLOAT64,
    data_source STRING
)
OPTIONS (
    format = 'CSV',
    skip_leading_rows = 1,
    uris = ['gs://musa5090-s26-goyal-data/air_quality/hourly/*.csv']
);

-- Hourly Observations — JSON-L
CREATE OR REPLACE EXTERNAL TABLE `musa-cloudcomputing-spring2026.air_quality.hourly_observations_jsonl`
(
    valid_date STRING,
    valid_time STRING,
    aqsid STRING,
    site_name STRING,
    gmt_offset FLOAT64,
    parameter_name STRING,
    reporting_units STRING,
    value FLOAT64,
    data_source STRING
)
OPTIONS (
    format = 'NEWLINE_DELIMITED_JSON',
    uris = ['gs://musa5090-s26-goyal-data/air_quality/hourly/*.jsonl']
);

-- Hourly Observations — Parquet
CREATE OR REPLACE EXTERNAL TABLE `musa-cloudcomputing-spring2026.air_quality.hourly_observations_parquet`
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://musa5090-s26-goyal-data/air_quality/hourly/*.parquet']
);

-- Site Locations — CSV
CREATE OR REPLACE EXTERNAL TABLE `musa-cloudcomputing-spring2026.air_quality.site_locations_csv`
(
    StationID STRING,
    AQSID STRING,
    FullAQSID STRING,
    Parameter STRING,
    MonitorType STRING,
    SiteCode STRING,
    SiteName STRING,
    Status STRING,
    AgencyID STRING,
    AgencyName STRING,
    EPARegion STRING,
    Latitude FLOAT64,
    Longitude FLOAT64,
    Elevation FLOAT64,
    GMTOffset FLOAT64,
    CountryFIPS STRING,
    CBSA_ID STRING,
    CBSA_Name STRING,
    StateAQSCode STRING,
    StateAbbreviation STRING,
    CountyAQSCode STRING,
    CountyName STRING
)
OPTIONS (
    format = 'CSV',
    skip_leading_rows = 1,
    uris = ['gs://musa5090-s26-goyal-data/air_quality/sites/site_locations.csv']
);

-- Site Locations — JSON-L
CREATE OR REPLACE EXTERNAL TABLE `musa-cloudcomputing-spring2026.air_quality.site_locations_jsonl`
OPTIONS (
    format = 'NEWLINE_DELIMITED_JSON',
    uris = ['gs://musa5090-s26-goyal-data/air_quality/sites/site_locations.jsonl']
);

-- Site Locations — GeoParquet
CREATE OR REPLACE EXTERNAL TABLE `musa-cloudcomputing-spring2026.air_quality.site_locations_geoparquet`
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://musa5090-s26-goyal-data/air_quality/sites/site_locations.geoparquet']
);

-- Cross-table join: average PM2.5 by state for 2024-07-01
SELECT
    s.StateAbbreviation,
    ROUND(AVG(h.value), 2) AS avg_pm25,
    COUNT(*) AS observation_count
FROM `musa-cloudcomputing-spring2026.air_quality.hourly_observations_parquet` h
JOIN `musa-cloudcomputing-spring2026.air_quality.site_locations_csv` s
    ON h.aqsid = s.AQSID
WHERE
    h.parameter_name = 'PM2.5'
    AND h.valid_date = '07/01/24'
    AND s.StateAbbreviation IS NOT NULL
    AND s.StateAbbreviation != ''
GROUP BY s.StateAbbreviation
ORDER BY avg_pm25 DESC;