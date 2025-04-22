<script>
  import { onMount, onDestroy } from 'svelte';
  import { sensorData, sensorMetadata, fetchInitialData, initializeWebSocket, closeWebSocketConnection, getFormattedValue } from '../stores/sensorStore.js';
  
  let currentData = {
    1: null, // Current Sensor
    2: null, // Temperature Sensor 
    3: null, // Humidity Sensor
    4: null  // Relay Status
  };
  
  let calculatedPower = null;
  let lastUpdateTime = null;
  let unsubscribe;
  let isButtonDisabled = false;
  
  // Calculate power (P = V * I) with voltage fixed at 12V
  function calculatePower() {
    if (currentData[1] && currentData[1].value) {
      return currentData[1].value * 12; // P = 12V * I
    }
    return null;
  }
  
  onMount(() => {
    // Subscribe to store updates
    unsubscribe = sensorData.subscribe(data => {
      // Get the latest value for each sensor
      Object.keys(currentData).forEach(sensorId => {
        if (data[sensorId] && data[sensorId].length > 0) {
          const newValue = data[sensorId][data[sensorId].length - 1];
          
          // Simply update all sensors directly
          currentData[sensorId] = newValue;
          
          // Update the last update time based on the most recent data point
          const timestamp = new Date(newValue.timestamp);
          if (!lastUpdateTime || timestamp > lastUpdateTime) {
            lastUpdateTime = timestamp;
          }
        }
      });
      
      // Calculate power whenever currentData is updated
      calculatedPower = calculatePower();
      
      // Force reactivity
      currentData = {...currentData};
    });
    
    // Then fetch data and establish WebSocket connection in the background
    setTimeout(() => {
      // Fetch initial data without blocking UI
      fetchInitialData().catch(err => console.error('Error fetching initial data:', err));
      
      // Initialize WebSocket connection
      initializeWebSocket();
    }, 100);
  });
  
  onDestroy(() => {
    if (unsubscribe) unsubscribe();
  });
  
  // Format timestamp nicely
  function formatTimestamp(timestamp) {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleString();
  }
  
  // Simplified function to control the motor
  async function toggleMotor() {
    if (isButtonDisabled) return;
    
    const isRunning = currentData[4] && currentData[4].value === 1;
    const command = isRunning ? 'stop' : 'start';
    
    // Disable button while request is processing
    isButtonDisabled = true;
    
    try {
      // Optimistically update the UI immediately
      const newValue = isRunning ? 0 : 1;
      
      if (currentData[4]) {
        currentData[4] = {
          ...currentData[4],
          value: newValue
        };
        currentData = {...currentData};
      }
      
      // Send command to backend - updated to use path parameter
      const response = await fetch(`/api/motor/control/${command}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to control motor');
      }
      
      // Just log the result, no need to wait for confirmation
      const result = await response.json();
      if (result.status !== 'success') {
        console.warn('Motor control response was not successful:', result.message);
      }
    } catch (error) {
      console.error('Error controlling motor:', error);
      alert('Error controlling motor: ' + error.message);
    } finally {
      // Re-enable button after request completes
      isButtonDisabled = false;
    }
  }
  
  // Simplified motor state function
  function getMotorState() {
    return currentData[4] && currentData[4].value === 1;
  }
  
  // Get current temperature value
  function getCurrentTemperature() {
    return currentData[2] ? currentData[2].value : null;
  }
</script>

<div class="container mx-auto p-4">
  <h3 class="text-2xl font-bold mb-6">Realtime Monitoring</h3>
  
  <div class="bg-white rounded shadow p-4 mb-6">
    <div class="flex justify-between items-center mb-4">
      <h4 class="text-xl mb-3">Sensor Status</h4>
      <p class="text-sm text-gray-500 mt-4 text-left">
        Last updated: {lastUpdateTime ? formatTimestamp(lastUpdateTime) : 'N/A'}
      </p>
    </div>
    
<div class="overflow-x-auto">
  <table class="min-w-full bg-white">
    <thead>
      <tr>
        <th class="py-2 px-4 border-b">Sensor</th>
        <th class="py-2 px-4 border-b">Value</th>
        <th class="py-2 px-4 border-b">Unit</th>
      </tr>
    </thead>
    <tbody>
      {#each Object.entries(sensorMetadata) as [id, sensor]}
        <tr class="{id == 2 && getCurrentTemperature() > 40 ? 'bg-red-50' : ''}">
          <td class="py-2 px-4 border-b">{sensor.name}</td>
          <td class="py-2 px-4 border-b">
            {#if currentData[id]}
              <span class="{id == 2 && getCurrentTemperature() > 40 ? 'text-red-600 font-semibold' : ''}">
                {getFormattedValue(id, currentData[id].value)}
              </span>
            {:else}
              N/A
            {/if}
          </td>
          <td class="py-2 px-4 border-b">{sensor.unit}</td>
        </tr>
        
        <!-- Insert power row right after current sensor (id 1) -->
        {#if id === '1'}
          <tr>
            <td class="py-2 px-4 border-b">Power</td>
            <td class="py-2 px-4 border-b">
              {#if calculatedPower !== null}
                {calculatedPower.toFixed(2)}
              {:else}
                N/A
              {/if}
            </td>
            <td class="py-2 px-4 border-b">W</td>
          </tr>
        {/if}
      {/each}
    </tbody>
  </table>
</div>
    <!-- Temperature Control Info Card -->
    <div class="mt-6 p-4 bg-gray-50 rounded-md border border-gray-200">
      <h5 class="text-md font-semibold mb-2">Automatic Temperature Control</h5>
      <ul class="list-disc list-inside text-sm text-gray-600 space-y-1">
        <li>Motor will start automatically when temperature exceeds 40°C</li>
        <li>Motor will stop automatically when temperature falls below 30°C</li>
        <li>Manual control will override automatic temperature control</li>
      </ul>
    </div>
    
    <!-- Motor control button -->
    <div class="mt-6 flex justify-start">
      <button 
        on:click={toggleMotor} 
        disabled={isButtonDisabled}
        class="px-6 py-2 rounded-md font-medium text-white shadow-sm focus:outline-none"
        class:bg-blue-500={!getMotorState()}
        class:bg-red-500={getMotorState()}
        class:opacity-50={isButtonDisabled}
      >
        {#if getMotorState()}
          Stop Motor
        {:else}
          Start Motor
        {/if}
        
        {#if isButtonDisabled}
          <span class="ml-2">...</span>
        {/if}
      </button>
    </div>
  </div>
  
  <p class="text-sm text-gray-600">
    Showing real-time data from all sensors. The dashboard page shows historical trends.
  </p>
</div>
