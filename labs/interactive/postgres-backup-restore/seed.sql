DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
  id integer PRIMARY KEY,
  name text NOT NULL,
  email text NOT NULL UNIQUE
);
INSERT INTO customers (id, name, email) VALUES
  (1, 'Alice', 'alice@example.test'),
  (2, 'Bob', 'bob@example.test'),
  (3, 'Carol', 'carol@example.test');
