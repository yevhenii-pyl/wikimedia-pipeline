import os
import json
import requests
from kafka import KafkaProducer

# Config
WIKI_STREAM_URL = os.getenv("WIKI_STREAM_URL")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_TOPIC_INPUT = os.getenv("KAFKA_TOPIC_INPUT")

def main():
    print(f"Connecting to Wikimedia stream: {WIKI_STREAM_URL}")
    print(f"Sending events to Kafka topic: {KAFKA_TOPIC_INPUT} at {KAFKA_BOOTSTRAP_SERVERS}")

    # Kafka producer
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    # Stream Wikimedia events
    with requests.get(WIKI_STREAM_URL, stream=True) as response:
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print(f"Received line: {decoded_line}")

                if decoded_line.startswith("data: "):
                    json_payload = decoded_line[6:]
                    try:
                        event = json.loads(json_payload)
                        producer.send(KAFKA_TOPIC_INPUT, value=event)
                        print(f"Sent event: {event.get('meta', {}).get('id', 'no-id')}")
                    except json.JSONDecodeError:
                        print("Failed to decode JSON in data line")
                else:
                    print(" Skipped non-data line")

if __name__ == "__main__":
    main()
