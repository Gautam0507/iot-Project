import logging
import mysql.connector
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from db_config import get_db_config


# Define models for the API responses
class SensorReading(BaseModel):
    id: int
    value: float
    timestamp: datetime


class SensorData(BaseModel):
    sensor_id: int
    sensor_name: str
    sensor_type: str
    readings: List[SensorReading]


def get_logger():
    """Get or create a module-level logger"""
    return logging.getLogger("sensor_data_access")


def get_sensor_by_id(
    sensor_id: int, logger: Optional[logging.Logger] = None
) -> Optional[Dict[str, Any]]:
    """
    Get sensor details from the database by ID
    Returns None if sensor not found
    """
    logger = logger or get_logger()
    db_config = get_db_config()

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, name, type FROM sensors WHERE id = %s", (sensor_id,))
        sensor = cursor.fetchone()

        cursor.close()
        conn.close()

        # If sensor is not a dictionary (e.g., it's a tuple), convert it to a dictionary
        if sensor and not isinstance(sensor, dict):
            column_names = ["id", "name", "type"]
            return dict(
                zip(column_names, sensor)
            )  # Return the converted dictionary directly

        # Ensure we're returning either Dict[str, Any] or None
        return sensor if isinstance(sensor, dict) else None
    except Exception as e:
        logger.error(f"Error retrieving sensor with ID {sensor_id}: {str(e)}")
        return None


def get_sensor_readings(
    sensor_id: int, logger: Optional[logging.Logger] = None
) -> List[Dict[str, Any]]:
    """
    Get all readings for a specific sensor by ID
    """
    logger = logger or get_logger()
    db_config = get_db_config()
    result_readings: List[Dict[str, Any]] = []  # Initialize with proper type annotation

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, value, timestamp 
            FROM sensor_data 
            WHERE sensor_id = %s
            ORDER BY timestamp DESC
        """,
            (sensor_id,),
        )

        readings = cursor.fetchall()

        # Ensure all readings are dictionaries
        for reading in readings:
            if isinstance(reading, dict):
                result_readings.append(reading)
            else:
                # Convert tuple to dictionary
                column_names = ["id", "value", "timestamp"]
                result_readings.append(dict(zip(column_names, reading)))

        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error retrieving readings for sensor ID {sensor_id}: {str(e)}")

    return result_readings  # Return the properly typed list


def get_complete_sensor_data(
    sensor_id: int, logger: Optional[logging.Logger] = None
) -> Optional[SensorData]:
    """
    Get complete sensor data including all readings by sensor ID
    Returns a SensorData object or None if sensor not found or error occurs
    """
    logger = logger or get_logger()

    # Get sensor details
    sensor = get_sensor_by_id(sensor_id, logger)
    if not sensor:
        logger.warning(f"Sensor with ID {sensor_id} not found")
        return None

    # Get readings for this sensor
    readings = get_sensor_readings(sensor_id, logger)

    # Create response object
    return SensorData(
        sensor_id=sensor["id"],
        sensor_name=sensor["name"],
        sensor_type=sensor["type"],
        readings=[SensorReading(**reading) for reading in readings],
    )


def get_recent_readings(
    logger: Optional[logging.Logger] = None,
) -> Dict[int, List[Dict[str, Any]]]:
    """
    Get the 50 most recent readings for each sensor in the database.

    Returns:
        Dict[int, List[Dict[str, Any]]]: A dictionary with sensor_id as key and list of readings as value
    """
    logger = logger or get_logger()
    db_config = get_db_config()
    result = {}

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # First, get all distinct sensor IDs
        cursor.execute("SELECT DISTINCT sensor_id FROM sensor_data")
        rows = cursor.fetchall()

        # Properly extract sensor_ids based on the row type
        sensor_ids = []
        for row in rows:
            if isinstance(row, dict):
                sensor_ids.append(row["sensor_id"])
            else:
                # Assuming sensor_id is the first column in the result
                sensor_ids.append(row[0])

        # For each sensor, get the 50 most recent readings
        for sensor_id in sensor_ids:
            cursor.execute(
                """
                SELECT id, sensor_id, value, timestamp 
                FROM sensor_data 
                WHERE sensor_id = %s
                ORDER BY timestamp DESC
                LIMIT 50
                """,
                (int(sensor_id),),  # Explicitly cast to int to ensure compatibility
            )
            readings = cursor.fetchall()

            # Ensure all readings are dictionaries
            result_readings = []
            for reading in readings:
                if not isinstance(reading, dict):
                    column_names = ["id", "sensor_id", "value", "timestamp"]
                    result_readings.append(dict(zip(column_names, reading)))
                else:
                    result_readings.append(reading)

            result[sensor_id] = result_readings

        cursor.close()
        conn.close()

        logger.info(f"Retrieved recent readings for {len(sensor_ids)} sensors")
        return result

    except Exception as e:
        logger.error(f"Error retrieving recent sensor readings: {str(e)}")
        return {}


def get_all_sensors(logger: Optional[logging.Logger] = None) -> List[Dict[str, Any]]:
    """
    Get all sensors from the database with their IDs and names.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing sensor information
    """
    logger = logger or get_logger()
    db_config = get_db_config()
    result_sensors: List[Dict[str, Any]] = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, name, type FROM sensors ORDER BY id")
        sensors = cursor.fetchall()

        # Ensure all sensors are dictionaries
        for sensor in sensors:
            if isinstance(sensor, dict):
                result_sensors.append(sensor)
            else:
                # Convert tuple to dictionary
                column_names = ["id", "name", "type"]
                result_sensors.append(dict(zip(column_names, sensor)))

        cursor.close()
        conn.close()

        logger.info(f"Retrieved {len(result_sensors)} sensors")
        return result_sensors

    except Exception as e:
        logger.error(f"Error retrieving sensors: {str(e)}")
        return []


def update_relay_state(state: int, logger: Optional[logging.Logger] = None) -> bool:
    """
    Update the relay state in the database

    Args:
        state: 1 for running/on, 0 for stopped/off
        logger: Optional logger instance

    Returns:
        bool: True if successful, False otherwise
    """
    logger = logger or get_logger()
    db_config = get_db_config()

    try:
        # Get the relay sensor ID (typically ID 4 based on your schema)
        relay_sensor_id = 4

        # Connect to database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert the new relay state
        now = datetime.now()
        cursor.execute(
            "INSERT INTO sensor_data (sensor_id, value, timestamp) VALUES (%s, %s, %s)",
            (relay_sensor_id, state, now),
        )

        conn.commit()
        logger.info(f"Updated relay state in database to {state}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        logger.error(f"Error updating relay state in database: {str(e)}")
        return False


def get_latest_relay_state(logger: Optional[logging.Logger] = None) -> Optional[int]:
    """
    Get the latest relay state (0 or 1) from the database

    Args:
        logger: Optional logger instance

    Returns:
        int: 1 if relay is on, 0 if relay is off, None if error or no data
    """
    logger = logger or get_logger()
    db_config = get_db_config()

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Get the most recent relay reading (sensor_id = 4)
        cursor.execute(
            """
            SELECT value FROM sensor_data 
            WHERE sensor_id = 4 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        )

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return 1 if result[0] == 1 or result[0] == True else 0
        else:
            return None

    except Exception as e:
        logger.error(f"Error getting latest relay state: {str(e)}")
        return None
