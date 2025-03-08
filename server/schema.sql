CREATE TABLE IF NOT EXISTS prefixes (
prefix VARCHAR(150) PRIMARY KEY,
bootstyle VARCHAR(150) NOT NULL,
sort_order INT DEFAULT 1);

CREATE TABLE IF NOT EXISTS tickets (
prefix VARCHAR(150),
ticket_id INT,
first_name VARCHAR(200),
last_name VARCHAR(200),
phone_number VARCHAR(200),
preference VARCHAR(100),
PRIMARY KEY (prefix, ticket_id)
);

CREATE TABLE IF NOT EXISTS baskets (
prefix VARCHAR(150),
basket_id INT,
description VARCHAR(255),
donors VARCHAR(255),
winning_ticket INT,
PRIMARY KEY (prefix, basket_id)
);

CREATE VIEW IF NOT EXISTS ticket_counts AS
SELECT prefix, COUNT(*) AS total_buys, COUNT(DISTINCT CONCAT(first_name, last_name, phone_number)) AS unique_buys
FROM tickets
GROUP BY prefix
UNION ALL
SELECT "totals", COUNT(*) AS total_buys, COUNT(DISTINCT CONCAT(first_name, last_name, phone_number)) AS unique_buys
FROM tickets;

CREATE VIEW IF NOT EXISTS basket_winners AS
SELECT b.*, CONCAT(t.last_name, ", ", t.first_name) AS winner_name, t.phone_number, t.preference
FROM baskets AS b
JOIN tickets AS t
ON b.prefix = t.prefix AND b.winning_ticket = t.ticket_id
ORDER BY b.prefix, b.basket_id;

CREATE TABLE IF NOT EXISTS api_keys (
api_key VARCHAR(255) PRIMARY KEY,
pc_name VARCHAR(255),
ip_addr VARCHAR(255));