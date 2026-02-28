"""@bruin

name: ingestion.trips
type: python
image: python:3.11

connection: duckdb-default

materialization:
  type: table
  strategy: append

@bruin"""

import os
import json
import io
import requests
import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import datetime


def materialize():
    """
    Fetches NYC Taxi trip data from the TLC public endpoint for the given
    date window and taxi types, and returns a single concatenated DataFrame.

    Bruin injects:
        BRUIN_START_DATE  – first day of the window (YYYY-MM-DD)
        BRUIN_END_DATE    – last day of the window  (YYYY-MM-DD)
        BRUIN_VARS        – JSON string with pipeline variables

    One parquet file is published per taxi_type per calendar month:
        https://d37ci6vzurychx.cloudfront.net/trip-data/<type>_tripdata_<YYYY>-<MM>.parquet
    """
    # --- Read Bruin runtime context ---
    start_date = datetime.strptime(os.environ["BRUIN_START_DATE"], "%Y-%m-%d")
    end_date   = datetime.strptime(os.environ["BRUIN_END_DATE"],   "%Y-%m-%d")
    taxi_types = json.loads(os.environ.get("BRUIN_VARS", "{}")).get("taxi_types", ["yellow"])

    base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data"

    # --- Generate (taxi_type, year, month) combos for the date window ---
    frames = []
    for taxi_type in taxi_types:
        current = start_date.replace(day=1)          # snap to first of month
        while current <= end_date:
            year  = current.strftime("%Y")
            month = current.strftime("%m")
            url   = f"{base_url}/{taxi_type}_tripdata_{year}-{month}.parquet"

            print(f"Fetching: {url}")
            try:
                response = requests.get(url, timeout=120)
                response.raise_for_status()

                df = pd.read_parquet(io.BytesIO(response.content))
                df["taxi_type"]    = taxi_type
                df["extracted_at"] = datetime.utcnow().isoformat()

                frames.append(df)
                print(f"  ✓ {len(df):,} rows loaded")

            except requests.HTTPError as e:
                print(f"  ⚠ Skipped {url}: {e}")

            current += relativedelta(months=1)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)
