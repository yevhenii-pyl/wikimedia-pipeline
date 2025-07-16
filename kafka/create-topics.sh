#!/bin/bash

# Create Kafka topics: input and processed
echo "Creating Kafka topics: input, processed..."

# Create 'input' topic
docker exec -it kafka kafka-topics.sh \
  --create \
  --topic input \
  --bootstrap-server kafka:9092 \
  --partitions 1 \
  --replication-factor 1

# Create 'processed' topic
docker exec -it kafka kafka-topics.sh \
  --create \
  --topic processed \
  --bootstrap-server kafka:9092 \
  --partitions 1 \
  --replication-factor 1

# List topics to verify
docker exec -it kafka kafka-topics.sh \
  --list \
  --bootstrap-server kafka:9092

echo "✅ Kafka topics created successfully."
