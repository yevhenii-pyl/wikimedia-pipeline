# Wikimedia Streaming Pipeline

This project implements a real-time data pipeline using:
- **Apache Kafka** (for message streaming)
- **Apache Spark Structured Streaming** (for processing)
- **Apache Cassandra** (for storage)
- **Docker Compose** (for orchestration)

---

### 1. Prerequisites
- Docker & Docker Compose installed
- Copy the environment file:
```bash
cp .env.template .env
```

### 2. Start the Stack

```bash 
docker compose --env-file .env up -d
```

```bash 
docker ps
```

You should see containers like:
```
zookeeper
kafka
cassandra
spark-master
spark-worker
```

### 3. Kafka Topics

Create the required topics:
```bash
./kafka/create-topics.sh
```

Verify:
```bash
docker exec -it kafka kafka-topics.sh --list --bootstrap-server kafka:9092
```

Expected:
```
input
processed
```

### 4. Cassandra 

Apply schema:
```bash
./cassandra/init-schema.sh
```

Verify keyspaces:
```bash
docker exec -it cassandra cqlsh -e "DESCRIBE KEYSPACES;"
```

Expected result:
```
system  system_auth  ...  wikimedia
```

Verify tables:

```bash
docker exec -it cassandra cqlsh -e "USE wikimedia; DESCRIBE TABLES;"
```

Expected result:
`page_creations`

### 5. Spark Master UI

Open http://localhost:8080 in your browser.
You should see the Spark Master web UI.

### 6. Final check

- Make sure the topics are created (step 3)
- Make sure DB table is created (step 4)
- Check that all containers are alive
- run
```bash
docker exec -it cassandra cqlsh -e "USE wikimedia; SELECT * FROM page_creations LIMIT 10;"
``` 