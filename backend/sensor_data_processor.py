import re
import logging
import mysql.connector
from datetime import datetime
from typing import Dict, List, Tuple, Optional


def get_db_config():
    return {
        "host": "localhost",  # Connect to the exposed Docker port on localhost
        "user": "root",
        "password": "secret",
        "database": "Sensor",
        "port": 3306,  # Explicitly set the port
    }


def get_logger() -> logging.Logger:
    """Get or create a module-level logger"""
    return logging.getLogger("sensor_processor")


def test_db_connection(logger: Optional[logging.Logger] = None):
    logger = logger or get_logger()
    db_config = get_db_config()

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sensors LIMIT 5")
        result = cursor.fetchall()
        logger.info(f"DB Connection Test - Found sensors: {result}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"DB Connection Test Failed: {str(e)}")
        return False


def parse_sensor_data(message: str) -> List[Tuple[str, float]]:
    """
    Parse the sensor data from the message.
    Format: "Current Sensor 1: 25.467, Temperature Sensor 1: 30.456"
    Returns a list of tuples (sensor_name, value)
    """
    # Split by comma and then parse each sensor reading
    sensor_readings = []

    # Handle multiple sensors separated by commas
    parts = [p.strip() for p in message.split(",")]

    for part in parts:
        # Extract sensor name and value using regex
        match = re.match(r"(.*?):\s*([-+]?\d*\.\d+|\d+)", part)
        if match:
            sensor_name = match.group(1).strip()
            value = float(match.group(2))
            sensor_readings.append((sensor_name, value))

    return sensor_readings


def get_sensor_ids(
    sensor_names: List[str], db_config: Dict, logger: Optional[logging.Logger] = None
) -> Dict[str, int]:
    """Get sensor IDs from the database based on sensor names"""
    logger = logger or get_logger()
    sensor_ids = {}

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Create a parameterized query with placeholders for all sensor names
        placeholders = ", ".join(["%s"] * len(sensor_names))
        query = f"SELECT id, name FROM sensors WHERE name IN ({placeholders})"

        cursor.execute(query, sensor_names)

        for sensor_id, sensor_name in cursor.fetchall():
            sensor_ids[sensor_name] = sensor_id

    except Exception as e:
        logger.error(f"Database error: {str(e)}")
    finally:
        if "cursor" in locals() and cursor:
            cursor.close()
        if "conn" in locals() and conn:
            conn.close()

    return sensor_ids


def insert_sensor_data(
    sensor_readings: List[Tuple[str, float]],
    db_config: Dict,
    logger: Optional[logging.Logger] = None,
):
    """Insert sensor readings into sensor_data table"""
    logger = logger or get_logger()

    if not sensor_readings:
        return

    # Extract just the sensor names for the lookup
    sensor_names = [reading[0] for reading in sensor_readings]

    # Get mapping of sensor names to IDs
    sensor_ids = get_sensor_ids(sensor_names, db_config, logger)

    # Prepare data for insertion
    now = datetime.now()
    values_to_insert = []

    for sensor_name, value in sensor_readings:
        if sensor_name in sensor_ids:
            values_to_insert.append((sensor_ids[sensor_name], value, now))

    if not values_to_insert:
        logger.warning("No valid sensor data to insert")
        return

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert all readings at once
        insert_query = """
            INSERT INTO sensor_data (sensor_id, value, timestamp) 
            VALUES (%s, %s, %s)
        """

        cursor.executemany(insert_query, values_to_insert)
        conn.commit()

        logger.info(f"Inserted {cursor.rowcount} sensor readings into database")

    except Exception as e:
        logger.error(f"Error inserting sensor data: {str(e)}")
    finally:
        if "cursor" in locals() and cursor:
            cursor.close()
        if "conn" in locals() and conn:
            conn.close()


def process_sensor_message(payload: str, logger: Optional[logging.Logger] = None):
    """Process an incoming sensor message, save to database, and return processed data"""
    logger = logger or get_logger()
    logger.info(f"RECEIVED PAYLOAD: {payload}")

    test_db_connection(logger)  # Test DB connection
    # Database connection configuration
    db_config = get_db_config()

    try:
        # Parse the message
        sensor_readings = parse_sensor_data(payload)
        logger.info(f"Parsed sensor readings: {sensor_readings}")

        # Insert into database
        insert_sensor_data(sensor_readings, db_config, logger)

        # Prepare data for WebSocket broadcast
        result = {"timestamp": datetime.now().isoformat(), "readings": []}

        # Get sensor IDs for the readings
        sensor_names = [reading[0] for reading in sensor_readings]
        sensor_ids = get_sensor_ids(sensor_names, db_config, logger)

        # Format data for WebSocket clients
        for sensor_name, value in sensor_readings:
            if sensor_name in sensor_ids:
                sensor_id = sensor_ids[sensor_name]
                result["readings"].append(
                    {"sensor_id": sensor_id, "sensor_name": sensor_name, "value": value}
                )

        return result
    except Exception as e:
        logger.error(f"Error processing sensor message: {str(e)}")
        return None
