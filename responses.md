# Assignment 03 Responses

## Part 4: BigQuery External Tables

### Hourly Observations — CSV External Table SQL

```sql
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
```

### Hourly Observations — JSON-L External Table SQL

```sql
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
```

### Hourly Observations — Parquet External Table SQL

```sql
CREATE OR REPLACE EXTERNAL TABLE `musa-cloudcomputing-spring2026.air_quality.hourly_observations_parquet`
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://musa5090-s26-goyal-data/air_quality/hourly/*.parquet']
);
```

### Site Locations — CSV External Table SQL

```sql
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
```

### Site Locations — JSON-L External Table SQL

```sql
CREATE OR REPLACE EXTERNAL TABLE `musa-cloudcomputing-spring2026.air_quality.site_locations_jsonl`
OPTIONS (
    format = 'NEWLINE_DELIMITED_JSON',
    uris = ['gs://musa5090-s26-goyal-data/air_quality/sites/site_locations.jsonl']
);
```

### Site Locations — GeoParquet External Table SQL

```sql
CREATE OR REPLACE EXTERNAL TABLE `musa-cloudcomputing-spring2026.air_quality.site_locations_geoparquet`
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://musa5090-s26-goyal-data/air_quality/sites/site_locations.geoparquet']
);
```

### Cross-Table Join Query

```sql
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
```

---

## Part 5: Hive-Partitioned External Tables

### Hourly Observations — CSV (hive-partitioned)

```sql
CREATE OR REPLACE EXTERNAL TABLE `musa-cloudcomputing-spring2026.air_quality.hourly_observations_csv_hive`
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
WITH PARTITION COLUMNS (airnow_date DATE)
OPTIONS (
    format = 'CSV',
    skip_leading_rows = 1,
    uris = ['gs://musa5090-s26-goyal-data/air_quality/hourly/csv/*'],
    hive_partition_uri_prefix = 'gs://musa5090-s26-goyal-data/air_quality/hourly/csv'
);
```

### Hourly Observations — JSON-L (hive-partitioned)

```sql
CREATE OR REPLACE EXTERNAL TABLE `musa-cloudcomputing-spring2026.air_quality.hourly_observations_jsonl_hive`
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
WITH PARTITION COLUMNS (airnow_date DATE)
OPTIONS (
    format = 'NEWLINE_DELIMITED_JSON',
    uris = ['gs://musa5090-s26-goyal-data/air_quality/hourly/jsonl/*'],
    hive_partition_uri_prefix = 'gs://musa5090-s26-goyal-data/air_quality/hourly/jsonl'
);
```

### Hourly Observations — Parquet (hive-partitioned)

```sql
CREATE OR REPLACE EXTERNAL TABLE `musa-cloudcomputing-spring2026.air_quality.hourly_observations_parquet_hive`
WITH PARTITION COLUMNS (airnow_date DATE)
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://musa5090-s26-goyal-data/air_quality/hourly/parquet/*'],
    hive_partition_uri_prefix = 'gs://musa5090-s26-goyal-data/air_quality/hourly/parquet'
);
```

---

## Part 6: Analysis & Reflection

### 1. File Sizes

**Hourly data (single day):**

| Format  | File Size |
|---------|-----------|
| CSV     | 17.6 MB   |
| JSON-L  | 41.7 MB   |
| Parquet | 0.8 MB    |

**Site locations:**

| Format     | File Size |
|------------|-----------|
| CSV        |  1.0 MB   |
| JSON-L     |  2.8MB    |
| GeoParquet |  0.5 MB   |

**Analysis:**
> [Your answer here — which is smallest/largest and why?]
Parquet is by far the smallest format in both cases. This is because Parquet is a binary columnar format that compresses data efficiently and stores each column together. JSON-L is the largest because it repeats every column name as a key in every single row, adding significant overhead.

### 2. Format Anatomy

> [Pick two formats and describe their structure. What are the key differences?]

CSV stores data as plain text rows with comma/pipe separators simple but verbose. Parquet stores data in binary columns with built-in compression, making it unreadable by humans but much faster and smaller for analytics.

### 3. Choosing Formats for BigQuery

> [Why is Parquet preferred over CSV or JSON-L? Consider performance and cost.]

Parquet is preferred because BigQuery only reads the columns a query needs and the built-in compression means less data scanned which directly reduces both query time and cost.

### 4. Pipeline vs. Warehouse Joins

> [You kept hourly data and site locations as separate tables and joined them in BigQuery. What if you had joined them during the prepare step instead (denormalization)? What are the trade-offs of each approach?]

Joining at query time (separate tables) keeps the pipeline flexible, you can change how you join without reprocessing the data but costs more per query since BigQuery has to join on the fly. Denormalizing during prepare makes queries faster and cheaper but means reprocessing all 31 days if the site locations data ever changes.

#### Stretch Challenge (optional)

If you implemented the stretch challenge (scripts `06_prepare`, `06_upload_to_gcs`, `06_create_tables.sql`), paste your SQL statements here:

```sql
-- Merged Hourly + Sites — CSV (hive-partitioned)
```

```sql
-- Merged Hourly + Sites — JSON-L (hive-partitioned)
```

```sql
-- Merged Hourly + Sites — GeoParquet (hive-partitioned)
```

### 5. Choosing a Data Source

For each person below, which air quality data source (AirNow hourly files, AirNow API, AQS bulk downloads, or AQS API) would you recommend, and why?

**a) A parent who wants a dashboard showing current air quality near their child's school:**
> AirNow API — provides real-time AQI data that can power a live dashboard with minimal setup.

**b) An environmental justice advocate identifying neighborhoods with chronically poor air quality over the past decade:**
> AQS bulk downloads — contains decades of historical monitoring data suitable for long-term trend analysis.

**c) A school administrator who needs automated morning alerts when AQI exceeds a threshold:**
> AirNow API — supports automated queries so alerts can be triggered programmatically each morning.
