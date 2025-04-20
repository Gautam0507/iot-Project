// src/stores/sensorStore.js
import { writable } from "svelte/store";

// Define sensor store with properly typed structure
export const sensorData = writable({
  1: [], // Current Sensor (float values)
  2: [], // Temperature Sensor (float values)
  3: [], // Humidity Sensor (float values)
  4: [], // Relay Status (0 or 1)
});

// Sensor metadata for display purposes
export const sensorMetadata = {
  1: { name: "Current Sensor", type: "current", unit: "A" },
  2: { name: "Temperature Sensor", type: "DHT22", unit: "°C" },
  3: { name: "Humidity Sensor", type: "DHT22", unit: "%" },
  4: { name: "Relay Status", type: "relay", unit: "" },
};

// API URL configuration - use relative paths for production
const API_BASE_URL = ""; // Empty for relative paths
const WEBSOCKET_URL = `ws://${window.location.host}/ws`;
let websocket = null;

// Function to fetch initial data from the API
export const fetchInitialData = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/recent_readings`);
    if (!response.ok) {
      throw new Error("Failed to fetch sensor data");
    }

    const result = await response.json();
    if (result.status === "success" && result.data) {
      // Process and update the store
      const formattedData = {};

      // Process each sensor's data
      Object.entries(result.data).forEach(([sensorId, readings]) => {
        // Convert string sensorId to number
        const id = parseInt(sensorId);

        // Format readings - ensure they are sorted by timestamp (oldest first)
        const formattedReadings = readings
          .map((reading) => ({
            id: reading.id,
            value: reading.value,
            timestamp: reading.timestamp,
          }))
          .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

        formattedData[id] = formattedReadings;
      });

      // Update the store
      sensorData.set(formattedData);
    }
  } catch (error) {
    console.error("Error fetching sensor data:", error);
  }
};

// Function to initialize WebSocket connection
export const initializeWebSocket = () => {
  if (websocket && websocket.readyState !== WebSocket.CLOSED) {
    return websocket; // Return existing connection
  }

  websocket = new WebSocket(WEBSOCKET_URL);

  websocket.onopen = () => {
    console.log("WebSocket connection established");

    // Setup heartbeat mechanism
    const heartbeatInterval = setInterval(() => {
      if (websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({ type: "heartbeat" }));
      } else {
        clearInterval(heartbeatInterval);
      }
    }, 30000); // Send heartbeat every 30 seconds
  };

  websocket.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data);

      // Handle heartbeat acknowledgment
      if (message.type === "heartbeat_ack") {
        return;
      }

      // Process incoming sensor readings
      if (message.readings && Array.isArray(message.readings)) {
        // Update store with new readings
        sensorData.update((currentData) => {
          message.readings.forEach((reading) => {
            const sensorId = reading.sensor_id;

            // Create new reading object
            const newReading = {
              id: Date.now(), // Use timestamp as ID if not provided
              value: reading.value,
              timestamp: message.timestamp || new Date().toISOString(),
            };

            // Ensure array exists for this sensor
            if (!currentData[sensorId]) {
              currentData[sensorId] = [];
            }

            // Add new reading and keep only the latest 50
            currentData[sensorId] = [
              ...currentData[sensorId],
              newReading,
            ].slice(-50);
          });

          return { ...currentData };
        });
      }
    } catch (error) {
      console.error("Error processing WebSocket message:", error);
    }
  };

  websocket.onclose = () => {
    console.log("WebSocket connection closed");
    // Attempt to reconnect after a delay
    setTimeout(() => {
      if (document.visibilityState !== "hidden") {
        initializeWebSocket();
      }
    }, 5000);
  };

  websocket.onerror = (error) => {
    console.error("WebSocket error:", error);
  };

  return websocket;
};

// Function to close WebSocket connection
export const closeWebSocketConnection = () => {
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    websocket.close();
  }
};

// Helper function to get latest reading for a sensor
export const getLatestReading = (sensorId) => {
  let readings = [];
  sensorData.subscribe((data) => {
    readings = data[sensorId] || [];
  })();

  return readings.length > 0 ? readings[readings.length - 1] : null;
};

// Function to get formatted value for display
export const getFormattedValue = (sensorId, value) => {
  if (sensorId === 4 || sensorId === "4") {
    // Relay status
    return value === 1 || value === true ? "Running" : "Stopped";
  } else {
    // Other sensors with decimal values
    return typeof value === "number" ? value.toFixed(2) : value;
  }
};
