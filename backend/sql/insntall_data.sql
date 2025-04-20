-- insert_sample_data.sql
USE fastapi_db;

-- Clear any existing data (optional)
-- DELETE FROM sensor_data;

-- Get the current date/time to base all timestamps on
SET @current_time = NOW();

-- Insert 20 values for Current Sensor (ID 1) - fluctuating between 2.1 and 3.5 amperes
INSERT INTO sensor_data (sensor_id, value, timestamp) VALUES 
(1, 2.43, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 20 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 2.51, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 19 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 2.58, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 18 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 2.71, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 17 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 2.85, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 16 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 3.02, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 15 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 3.15, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 14 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 3.28, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 13 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 3.41, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 12 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 3.35, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 11 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 3.21, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 10 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 3.08, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 9 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 2.95, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 8 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 2.78, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 7 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 2.67, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 6 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 2.53, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 5 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 2.42, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 4 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 2.38, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 3 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 2.46, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 2 MINUTE), '%Y-%m-%d %H:%i:%s')),
(1, 2.57, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 1 MINUTE), '%Y-%m-%d %H:%i:%s'));

-- Insert 20 values for Temperature Sensor (ID 2) - showing a gradual increase from 21 to 26 degrees Celsius
INSERT INTO sensor_data (sensor_id, value, timestamp) VALUES 
(2, 21.2, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 20 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 21.4, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 19 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 21.7, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 18 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 22.0, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 17 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 22.3, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 16 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 22.6, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 15 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 23.0, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 14 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 23.3, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 13 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 23.7, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 12 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 24.1, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 11 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 24.5, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 10 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 24.8, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 9 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 25.1, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 8 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 25.4, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 7 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 25.6, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 6 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 25.7, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 5 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 25.8, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 4 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 25.9, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 3 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 26.0, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 2 MINUTE), '%Y-%m-%d %H:%i:%s')),
(2, 25.9, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 1 MINUTE), '%Y-%m-%d %H:%i:%s'));

-- Insert 20 values for Humidity Sensor (ID 3) - fluctuating between 45% and 55%
INSERT INTO sensor_data (sensor_id, value, timestamp) VALUES 
(3, 46.8, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 20 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 47.2, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 19 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 48.1, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 18 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 49.5, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 17 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 50.7, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 16 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 51.8, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 15 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 52.9, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 14 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 54.1, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 13 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 54.8, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 12 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 55.0, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 11 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 54.6, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 10 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 53.9, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 9 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 52.7, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 8 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 51.4, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 7 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 50.5, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 6 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 49.2, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 5 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 48.1, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 4 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 47.5, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 3 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 47.0, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 2 MINUTE), '%Y-%m-%d %H:%i:%s')),
(3, 46.5, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 1 MINUTE), '%Y-%m-%d %H:%i:%s'));

-- Insert 20 values for Relay Status (ID 4) - showing ON (1) and OFF (0) periods
INSERT INTO sensor_data (sensor_id, value, timestamp) VALUES 
(4, 1, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 20 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 1, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 19 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 1, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 18 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 1, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 17 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 1, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 16 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 0, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 15 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 0, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 14 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 0, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 13 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 0, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 12 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 0, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 11 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 1, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 10 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 1, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 9 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 1, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 8 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 1, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 7 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 1, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 6 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 0, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 5 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 0, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 4 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 0, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 3 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 1, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 2 MINUTE), '%Y-%m-%d %H:%i:%s')),
(4, 1, DATE_FORMAT(DATE_SUB(@current_time, INTERVAL 1 MINUTE), '%Y-%m-%d %H:%i:%s'));

-- Verify data was inserted
SELECT 'Current Sensor data:' as '';
SELECT sensor_id, value, timestamp FROM sensor_data WHERE sensor_id = 1 ORDER BY timestamp DESC LIMIT 5;

SELECT 'Temperature Sensor data:' as '';
SELECT sensor_id, value, timestamp FROM sensor_data WHERE sensor_id = 2 ORDER BY timestamp DESC LIMIT 5;

SELECT 'Humidity Sensor data:' as '';
SELECT sensor_id, value, timestamp FROM sensor_data WHERE sensor_id = 3 ORDER BY timestamp DESC LIMIT 5;

SELECT 'Relay Status data:' as '';
SELECT sensor_id, value, timestamp FROM sensor_data WHERE sensor_id = 4 ORDER BY timestamp DESC LIMIT 5;
