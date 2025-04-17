import logging
import asyncio
import json
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from mqtt_client import MQTTHandler
from sensor_data_access import (
    get_complete_sensor_data,
    SensorData,
    get_recent_readings,
    get_all_sensors,
)
from web_sockets import ConnectionManager
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("app")

# Create FastAPI app
app = FastAPI(title="MQTT Listener")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/data"
SENSOR_DATA_TOPIC = "sensors/data"  # Topic for sensor data

# Create MQTT client
mqtt_handler = MQTTHandler(
    broker=MQTT_BROKER, port=MQTT_PORT, client_id="fastapi_mqtt_client", logger=logger
)

manager = ConnectionManager()

latest_sensor_data: Optional[Dict[str, Any]] = None
latest_sensor_data_lock = asyncio.Lock()  # For thread safety


# Function to update the latest sensor data (called from MQTT handler)
def set_latest_sensor_data(data: Dict[str, Any]):
    global latest_sensor_data
    latest_sensor_data = data


# Setup startup and shutdown events
@app.on_event("startup")
async def startup_event():
    mqtt_handler.start()
    mqtt_handler.subscribe(MQTT_TOPIC)  # Subscribe to the main topic
    mqtt_handler.subscribe(SENSOR_DATA_TOPIC)  # Subscribe to sensor data topic
    logger.info(f"Subscribed to sensor data topic: {SENSOR_DATA_TOPIC}")


@app.on_event("shutdown")
async def shutdown_event():
    mqtt_handler.stop()


# Dependency to ensure MQTT is connected
def verify_mqtt_connection():
    if not mqtt_handler.is_connected():
        return JSONResponse(
            status_code=503, content={"error": "MQTT service unavailable"}
        )
    return True


# Basic routes
@app.get("/")
async def read_root():
    return {"message": "MQTT listener running. Check server logs for MQTT messages."}


@app.get("/status")
async def get_mqtt_status():
    return {
        "status": "connected" if mqtt_handler.is_connected() else "disconnected",
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
    Get recent 50 readings for  initalizing the website
    """
    readings = get_recent_readings(logger)

    if not readings:
        raise HTTPException(status_code=404, detail=f"No readings found ")

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

    # Track data that's been sent to this specific client
    last_sent_data = None

    # Set up heartbeat timeout detection
    last_heartbeat = asyncio.get_running_loop().time()
    heartbeat_timeout = 120  # seconds to wait for heartbeat before closing connection

    try:
        while True:
            # Check for new sensor data
            global latest_sensor_data

            # Send new sensor data if available
            if latest_sensor_data is not None and latest_sensor_data != last_sent_data:
                await websocket.send_json(latest_sensor_data)
                last_sent_data = latest_sensor_data

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


# Entry point for Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
