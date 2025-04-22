import logging
import asyncio
import json
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    Request,
)
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles  # Import for serving static files

from mqtt_client import MQTTHandler
from sensor_data_access import (
    get_complete_sensor_data,
    SensorData,
    get_recent_readings,
    update_relay_state,
    get_all_sensors,
    get_latest_relay_state,
)
from web_sockets import ConnectionManager
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
import uvicorn
from datetime import datetime
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("app")

# Define the static files directory
STATIC_DIR = Path(__file__).parent.parent / "frontend" / "dist"

# Create FastAPI app
app = FastAPI(title="MQTT Listener")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static files directory
app.mount("/assets", StaticFiles(directory=f"{STATIC_DIR}/assets"), name="assets")

# MQTT Configuration
MQTT_BROKER = "192.168.62.88"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/data"
SENSOR_DATA_TOPIC = "sensors/data"

# Create connection manager for WebSockets
manager = ConnectionManager()

# Global variable to store latest sensor data
latest_sensor_data: Optional[Dict[str, Any]] = None
latest_sensor_data_lock = asyncio.Lock()

# Create MQTT client - will be initialized in startup event
mqtt_handler = None

# Variables to track temperature-based motor control state
motor_started_by_temperature = False
last_temperature_reading = None
last_motor_state = None


# Function to handle temperature-based motor control
async def handle_temperature_based_control(temperature, current_motor_state):
    # Existing code remains unchanged
    # ...
    global motor_started_by_temperature, last_temperature_reading, last_motor_state

    # Update tracking variables
    last_temperature_reading = temperature
    last_motor_state = current_motor_state

    # Case 1: Temperature > 40°C - Start motor if not already running
    if temperature > 40 and not current_motor_state:
        logger.info(
            f"Temperature ({temperature}°C) exceeds threshold of 40°C. Starting motor automatically."
        )

        # Update the relay state to 1 (on)
        success = update_relay_state(1, logger)
        if success:
            motor_started_by_temperature = True

            # Prepare data for WebSocket broadcast
            timestamp = datetime.now().isoformat()
            message = {
                "timestamp": timestamp,
                "readings": [
                    {
                        "sensor_id": 4,  # Relay sensor ID
                        "sensor_name": "Relay Status",
                        "value": 1,
                    }
                ],
                "alert": {
                    "type": "temperature_high",
                    "message": f"Temperature ({temperature}°C) exceeded threshold of 40°C. Motor started automatically.",
                    "temperature": temperature,
                    "action": "motor_started",
                },
            }

            # Broadcast to WebSocket clients
            await manager.broadcast(message)

            # Also publish to MQTT
            if mqtt_handler:
                mqtt_handler.publish("motor/control", "start")

            logger.info("Motor started automatically due to high temperature")
            return True

    # Case 2: Temperature < 30°C - Stop motor only if it was started by temperature
    elif temperature < 30 and current_motor_state and motor_started_by_temperature:
        logger.info(
            f"Temperature ({temperature}°C) fell below threshold of 30°C. Stopping motor automatically."
        )

        # Update the relay state to 0 (off)
        success = update_relay_state(0, logger)
        if success:
            motor_started_by_temperature = False

            # Prepare data for WebSocket broadcast
            timestamp = datetime.now().isoformat()
            message = {
                "timestamp": timestamp,
                "readings": [
                    {
                        "sensor_id": 4,  # Relay sensor ID
                        "sensor_name": "Relay Status",
                        "value": 0,
                    }
                ],
                "alert": {
                    "type": "temperature_normal",
                    "message": f"Temperature ({temperature}°C) fell below threshold of 30°C. Motor stopped automatically.",
                    "temperature": temperature,
                    "action": "motor_stopped",
                },
            }

            # Broadcast to WebSocket clients
            await manager.broadcast(message)

            # Also publish to MQTT
            if mqtt_handler:
                mqtt_handler.publish("motor/control", "stop")

            logger.info(
                "Motor stopped automatically due to temperature returning to normal"
            )
            return True

    return False


# Function to update the latest sensor data (called from MQTT handler)
def set_latest_sensor_data(data: Dict[str, Any]):
    global latest_sensor_data
    latest_sensor_data = data
    logger.info("Latest sensor data updated")


# Setup startup and shutdown events
@app.on_event("startup")
async def startup_event():
    # Existing code remains unchanged
    # ...
    global mqtt_handler
    # Get the current event loop
    loop = asyncio.get_running_loop()
    logger.info(f"App startup - Event loop: {loop}")

    # Create MQTT handler
    mqtt_handler = MQTTHandler(
        broker=MQTT_BROKER,
        port=MQTT_PORT,
        client_id="fastapi_mqtt_client",
        logger=logger,
    )

    # Pass the event loop to MQTT handler
    mqtt_handler.set_event_loop(loop)

    # Start MQTT client
    mqtt_handler.start()
    mqtt_handler.subscribe(MQTT_TOPIC)  # Subscribe to the main topic
    mqtt_handler.subscribe(SENSOR_DATA_TOPIC)  # Subscribe to sensor data topic
    logger.info(f"Subscribed to sensor data topic: {SENSOR_DATA_TOPIC}")


@app.on_event("shutdown")
async def shutdown_event():
    global mqtt_handler
    if mqtt_handler:
        mqtt_handler.stop()


# Dependency to ensure MQTT is connected
def verify_mqtt_connection():
    if not mqtt_handler or not mqtt_handler.is_connected():
        return JSONResponse(
            status_code=503, content={"error": "MQTT service unavailable"}
        )
    return True


# Serve the SPA frontend ONLY at the root
@app.get("/", response_class=HTMLResponse)
async def serve_spa():
    """Serves the Single Page Application"""
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse(
            content="Frontend not built. Run 'npm run build' in the frontend directory.",
            status_code=500,
        )

    with open(index_path) as f:
        return HTMLResponse(content=f.read())


# API routes
@app.get("/status")
async def get_mqtt_status():
    # Keep the existing implementation
    # ...
    return {
        "status": (
            "connected"
            if mqtt_handler and mqtt_handler.is_connected()
            else "disconnected"
        ),
        "broker": MQTT_BROKER,
        "port": MQTT_PORT,
        "topics": [MQTT_TOPIC, SENSOR_DATA_TOPIC],
    }


@app.get("/subscribe/{topic}")
async def subscribe_to_topic(topic: str, _: bool = Depends(verify_mqtt_connection)):
    success = mqtt_handler.subscribe(topic)
    if success:
        return {"status": "success", "message": f"Subscribed to {topic}"}
    else:
        return {"status": "error", "message": "Failed to subscribe"}


@app.get("/sensor/{sensor_id}", response_model=SensorData)
async def get_sensor_data(sensor_id: int):
    """
    Get all data for a specific sensor identified by its ID.
    Returns sensor details and all readings with timestamps.
    """
    sensor_data = get_complete_sensor_data(sensor_id, logger)

    if not sensor_data:
        raise HTTPException(
            status_code=404, detail=f"Sensor with ID {sensor_id} not found"
        )

    return sensor_data


@app.get("/api/recent_readings")
async def get_init_readings():
    """
    Get recent 50 readings for initializing the website
    """
    readings = get_recent_readings(logger)

    if not readings:
        raise HTTPException(status_code=404, detail=f"No readings found")

    return {
        "status": "success",
        "message": "Recent readings retrieved successfully",
        "data": readings,
    }


@app.get("/api/get_sensors")
async def get_sensors():
    sensors = get_all_sensors(logger)
    if not sensors:
        return JSONResponse(content={"sensors": []}, status_code=200)
    return sensors


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    logger.info(
        f"New WebSocket connection established. Total connections: {len(manager.active_connections)}"
    )

    # Track data that's been sent to this specific client
    last_sent_data = None

    # Set up heartbeat timeout detection
    last_heartbeat = asyncio.get_running_loop().time()
    heartbeat_timeout = (
        300  # 5 minutes (300 seconds) to wait for heartbeat before closing connection
    )

    try:
        while True:
            # Check for new sensor data
            global latest_sensor_data

            # Process and send new sensor data if available
            if latest_sensor_data is not None and latest_sensor_data != last_sent_data:
                # Check for temperature sensor data and handle temperature-based control
                temperature_reading = None
                current_motor_state = None

                # Extract temperature and motor state if available
                if "readings" in latest_sensor_data:
                    for reading in latest_sensor_data["readings"]:
                        if reading["sensor_id"] == 2:  # Temperature sensor
                            temperature_reading = reading["value"]
                        elif reading["sensor_id"] == 4:  # Relay status
                            current_motor_state = reading["value"] == 1

                # If we have temperature data, process it for motor control
                if temperature_reading is not None:
                    # Query current motor state if not included in the current data
                    if current_motor_state is None:
                        # Get the most recent relay state from the database
                        current_motor_state = get_latest_relay_state(logger) == 1

                    # Handle temperature-based control
                    await handle_temperature_based_control(
                        temperature_reading, current_motor_state
                    )

                await websocket.send_json(latest_sensor_data)
                last_sent_data = latest_sensor_data
                logger.debug("Sent new sensor data to client")

            # Check if client heartbeat has timed out
            current_time = asyncio.get_running_loop().time()
            if current_time - last_heartbeat > heartbeat_timeout:
                logger.info(
                    f"WebSocket client heartbeat timeout after {heartbeat_timeout}s, closing connection"
                )
                break  # Exit the loop to close the connection

            # Listen for client messages with a reasonable timeout
            try:
                # Wait for client message - either data or a heartbeat
                data = await asyncio.wait_for(websocket.receive_text(), timeout=15.0)

                # Process received message
                if data:
                    try:
                        message = json.loads(data)
                        # Check if this is a heartbeat from client
                        if message.get("type") == "heartbeat":
                            last_heartbeat = current_time
                            # Optionally respond to heartbeat
                            await websocket.send_json({"type": "heartbeat_ack"})
                            logger.debug("Received heartbeat from client")
                        # Handle other message types here if needed
                    except json.JSONDecodeError:
                        logger.warning("Received invalid JSON from WebSocket client")

            except asyncio.TimeoutError:
                # This timeout just means no message received yet - not an error
                pass

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        # Make sure we always clean up the connection
        manager.disconnect(websocket)
        logger.info(
            f"WebSocket connection closed. Remaining connections: {len(manager.active_connections)}"
        )


@app.post("/api/motor/control/{command}")
async def control_motor(command: str):
    """
    Control motor by publishing to MQTT topic
    Command is received as a path parameter: /api/motor/control/start
    """
    global motor_started_by_temperature

    logger.info(f"Motor control request received with command: {command}")

    if command not in ["start", "stop"]:
        logger.warning(f"Invalid motor command received: {command}")
        raise HTTPException(
            status_code=400, detail="Invalid command. Use 'start' or 'stop'"
        )

    if not mqtt_handler:
        raise HTTPException(status_code=503, detail="MQTT service not initialized")

    # Map command to relay state (1 for start, 0 for stop)
    relay_state = 1 if command == "start" else 0

    # If stopping manually, reset the temperature flag
    if command == "stop":
        motor_started_by_temperature = False

    # Update database with new relay state
    db_updated = update_relay_state(relay_state, logger)
    if not db_updated:
        logger.warning(
            "Failed to update relay state in database, continuing with MQTT publish"
        )

    # Send command via MQTT
    success = mqtt_handler.publish("motor/control", command)
    if success:
        # Create sensor data for WebSockets
        # Prepare data for WebSocket broadcast
        sensor_data = {
            "timestamp": datetime.now().isoformat(),
            "readings": [
                {
                    "sensor_id": 4,  # Relay sensor ID
                    "sensor_name": "Relay Status",
                    "value": relay_state,
                }
            ],
        }

        # Update latest sensor data and broadcast to clients
        global latest_sensor_data
        latest_sensor_data = sensor_data
        asyncio.create_task(manager.broadcast(sensor_data))

        logger.info(f"Motor {command} command sent successfully")
        return {
            "status": "success",
            "message": f"Motor {command} command sent successfully",
        }
    else:
        logger.error("Failed to send motor control command")
        raise HTTPException(
            status_code=500, detail="Failed to send motor control command"
        )


# Entry point for Uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
