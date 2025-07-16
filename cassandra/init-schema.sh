#!/bin/bash

echo "⏳ Waiting for Cassandra to start..."

# Wait until cassandra responds
until docker exec cassandra cqlsh -e "describe keyspaces" >/dev/null 2>&1; do
  sleep 5
  echo "⌛ Still waiting..."
done

echo "✅ Cassandra is up. Applying schema..."

# Apply schema
docker exec -i cassandra cqlsh < cassandra/init.cql

echo "✅ Schema applied successfully."

# Verify
echo "🔍 Verifying schema..."
docker exec -it cassandra cqlsh -e "DESCRIBE KEYSPACES;"
