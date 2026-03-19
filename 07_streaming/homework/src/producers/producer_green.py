import pandas as pd
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
import json
import decimal
from dataclasses import dataclass, asdict
from time import time
import math

# --- 1. Dataclass Definition (Workshop Style) ---
@dataclass
class GreenRide:
    lpep_pickup_datetime: str
    lpep_dropoff_datetime: str
    PULocationID: int
    DOLocationID: int
    passenger_count: float  # Using float to handle potential nulls
    trip_distance: float
    tip_amount: float
    total_amount: float

    @classmethod
    def from_row(cls, row):
        # We handle NaNs here by converting them to None manually
        return cls(
            lpep_pickup_datetime=row['lpep_pickup_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
            lpep_dropoff_datetime=row['lpep_dropoff_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
            PULocationID=int(row['PULocationID']),
            DOLocationID=int(row['DOLocationID']),
            # Check for NaN and convert to None for JSON compatibility
            passenger_count=float(row['passenger_count']) if not math.isnan(row['passenger_count']) else None,
            trip_distance=float(row['trip_distance']),
            tip_amount=float(row['tip_amount']),
            total_amount=float(row['total_amount'])
        )

# --- 2. Topic Creation Section ---
def setup_topic(topic_name):
    admin_client = KafkaAdminClient(bootstrap_servers="localhost:9092")
    if topic_name not in admin_client.list_topics():
        print(f"Creating topic: {topic_name}")
        new_topic = NewTopic(name=topic_name, num_partitions=1, replication_factor=1)
        admin_client.create_topics([new_topic])
    else:
        print(f"Topic {topic_name} already exists.")
    admin_client.close()

# --- 3. Ingestion Section ---
def run_producer(topic_name, data_path):
    # Kafka Producer Setup with custom serializer
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    # Load Data
    print(f"Reading data from {data_path}...")
    columns = [
        'lpep_pickup_datetime', 'lpep_dropoff_datetime', 'PULocationID', 
        'DOLocationID', 'passenger_count', 'trip_distance', 
        'tip_amount', 'total_amount'
    ]
    df = pd.read_parquet(data_path, columns=columns)

    print(f"Starting to send {len(df)} records...")
    t0 = time()

    # Iterate using the Dataclass pattern
    for _, row in df.iterrows():
        ride = GreenRide.from_row(row)
        producer.send(topic_name, value=asdict(ride))

    producer.flush()
    t1 = time()

    print(f'Sending took {(t1 - t0):.2f} seconds')
    producer.close()

if __name__ == "__main__":
    TOPIC = "green-trips"
    DATA_FILE = "green_tripdata_2025-10.parquet"
    
    setup_topic(TOPIC)
    run_producer(TOPIC, DATA_FILE)
