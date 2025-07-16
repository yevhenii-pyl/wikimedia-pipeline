CREATE KEYSPACE IF NOT EXISTS wikimedia WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

USE wikimedia;

CREATE TABLE IF NOT EXISTS page_creations (
  user_id text,
  domain text,
  created_at timestamp,
  page_title text,
  PRIMARY KEY ((domain), created_at, user_id)
);
