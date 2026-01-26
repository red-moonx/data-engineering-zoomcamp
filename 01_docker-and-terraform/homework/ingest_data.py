#!/usr/bin/env python
# coding: utf-8

import click
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm

dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]


@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--target-table', required=True, help='Target table name')
@click.option('--file-path', required=True, help='Path to the data file (CSV or Parquet)')
@click.option('--chunksize', default=100000, type=int, help='Chunk size for reading CSV')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table, file_path, chunksize):
    """Ingest NYC taxi data into PostgreSQL database."""
    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    print(f"Loading data from {file_path}...")
    
    if file_path.endswith('.parquet'):
        # For Parquet, we load the whole file (1.1MB is small enough)
        df = pd.read_parquet(file_path)
        
        # Ensure date columns are datetime (Green taxi uses lpep)
        for col in df.columns:
            if 'datetime' in col:
                df[col] = pd.to_datetime(df[col])
        
        print(f"Ingesting {len(df)} rows into {target_table}...")
        df.head(0).to_sql(name=target_table, con=engine, if_exists='replace')
        df.to_sql(name=target_table, con=engine, if_exists='append')
    else:
        # For CSV, use the chunking logic from the workshop
        df_iter = pd.read_csv(
            file_path,
            iterator=True,
            chunksize=chunksize,
        )
        
        first = True
        for df_chunk in tqdm(df_iter):
            # Ensure date columns are datetime
            for col in df_chunk.columns:
                if 'datetime' in col:
                    df_chunk[col] = pd.to_datetime(df_chunk[col])
            
            if first:
                df_chunk.head(0).to_sql(name=target_table, con=engine, if_exists='replace')
                first = False
            
            df_chunk.to_sql(name=target_table, con=engine, if_exists='append')

    print(f"Successfully ingested data into {target_table}")

if __name__ == '__main__':
    run()