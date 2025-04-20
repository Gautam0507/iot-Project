-- insert_sample_sensor.sql
USE fastapi_db;

-- Insert a current sensor
INSERT INTO sensors (name, type) VALUES ('Current Sensor', 'current');
INSERT INTO sensors (name, type) VALUES ('Temperature Sensor', 'DHT22');
INSERT INTO sensors (name, type) VALUES ('Humidity Sensor', 'DHT22');
INSERT INTO sensors (name, type) VALUES ('Relay Status', 'relay');


-- Verify the sensor was inserted
SELECT * FROM sensor;
