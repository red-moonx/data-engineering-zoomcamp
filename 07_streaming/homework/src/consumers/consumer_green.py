import json
import logging
from kafka import KafkaConsumer

# Setup logging for better visibility
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_consumer(topic_name):
    """
    Kafka consumer to read 'green-trips' topic and count trips 
    with trip_distance greater than 5.0.
    """
    # 1. Consumer Configuration
    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',  # Start reading from the very beginning
        enable_auto_commit=True,
        group_id='homework-consumer-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        # Timeout of 1s ensures the consumer stops after reading all existing messages
        consumer_timeout_ms=1000
    )

    logger.info(f"Connecting to topic: {topic_name}")
    logger.info("Iterating over messages to count trips with trip_distance > 5.0...")

    trip_count = 0
    total_processed = 0

    try:
        # 2. Main Consumer Loop
        for message in consumer:
            trip_data = message.value
            total_processed += 1
            
            # Question 3 logic: trip_distance > 5.0
            if trip_data.get('trip_distance', 0) > 5.0:
                trip_count += 1
                
            # Print progress every 10k messages
            if total_processed % 10000 == 0:
                logger.info(f"Processed {total_processed} messages so far...")
                
    except Exception as e:
        logger.error(f"An error occurred during consumption: {e}")
    finally:
        consumer.close()

    # 3. Final Summary Report
    print("\n" + "="*40)
    print("      KAFKA CONSUMER REPORT")
    print("="*40)
    print(f"Total messages processed: {total_processed}")
    print(f"Trips with distance > 5.0: {trip_count}")
    print("="*40)
    print("End of processing.")

if __name__ == "__main__":
    TOPIC = "green-trips"
    run_consumer(TOPIC)
