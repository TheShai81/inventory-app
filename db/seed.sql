USE inventory_db;

INSERT INTO inventory (item_name, amount) VALUES
('apple', 100),
('banana', 50),
('orange', 75),
('milk', 80)
ON DUPLICATE KEY UPDATE amount = VALUES(amount);
