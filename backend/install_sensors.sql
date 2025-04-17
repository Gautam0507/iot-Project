-- insert_sample_sensor.sql
USE Sensor;

-- Insert a current sensor
INSERT INTO sensors (name, type) VALUES ('Current Sensor 1', 'current');
INSERT INTO sensors (name, type) VALUES ('Temperature Sensor 1', 'temperature');


-- Verify the sensor was inserted
SELECT * FROM sensors;
