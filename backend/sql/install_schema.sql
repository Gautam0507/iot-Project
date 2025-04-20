-- install_schema.sql
-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS fastapi_db;
USE fastapi_db;

-- Create sensors table
CREATE TABLE IF NOT EXISTS sensors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sensor_data table with foreign key reference
CREATE TABLE IF NOT EXISTS sensor_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT NOT NULL,
    value DOUBLE NOT NULL,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
        ON DELETE CASCADE
);
