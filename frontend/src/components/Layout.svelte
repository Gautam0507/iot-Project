<script>
  import { link } from 'svelte-spa-router';
  import { onMount, onDestroy } from 'svelte';
  import { sensorData, sensorMetadata, fetchInitialData, initializeWebSocket, closeWebSocketConnection, getFormattedValue } from '../stores/sensorStore.js';
  
  let websocket;
  let unsubscribe;
  
  // Track temperature alerts
  let temperatureAlert = null;
  let alertTimeout = null;
  
onMount(async () => {
  // Fetch initial data
  await fetchInitialData();
  
  // Initialize WebSocket connection once at layout level
  websocket = initializeWebSocket();
  
  // Subscribe to store updates
  unsubscribe = sensorData.subscribe((data) => {
    // Check the latest temperature reading
    if (data[2] && data[2].length > 0) {
      const latestTemperature = data[2][data[2].length - 1].value;
      
      // Check if we need to show an alert
      if (latestTemperature > 40 && (!temperatureAlert || temperatureAlert.type !== 'temperature_high')) {
        temperatureAlert = {
          type: 'temperature_high',
          message: `High temperature alert: ${latestTemperature.toFixed(1)}°C`,
          temperature: latestTemperature
        };
        
        // Clear any existing timeout
        if (alertTimeout) clearTimeout(alertTimeout);
        
        // Auto-dismiss after 30 seconds
        alertTimeout = setTimeout(() => {
          temperatureAlert = null;
        }, 30000);
      } 
      else if (latestTemperature < 30 && temperatureAlert && temperatureAlert.type === 'temperature_high') {
        temperatureAlert = {
          type: 'temperature_normal',
          message: `Temperature returned to normal: ${latestTemperature.toFixed(1)}°C`,
          temperature: latestTemperature
        };
        
        // Clear any existing timeout
        if (alertTimeout) clearTimeout(alertTimeout);
        
        // Auto-dismiss after 30 seconds
        alertTimeout = setTimeout(() => {
          temperatureAlert = null;
        }, 30000);
      }
    }
  });
});
  
  onDestroy(() => {
    // Clean up resources
    if (unsubscribe) unsubscribe();
    closeWebSocketConnection();
    
    // Clear any timers
    if (alertTimeout) {
      clearTimeout(alertTimeout);
    }
  });
</script>

<div class="flex flex-col min-h-screen bg-gray-100 text-gray-800">
  <!-- Navbar -->
  <nav class="bg-gray-800 p-4 shadow-md">
    <div class="container mx-auto flex justify-between items-center">
      <div class="text-white text-xl font-bold">Home Automation</div>
      <ul class="flex space-x-6">
        <li><a class="text-white hover:text-gray-300 transition" href="/dashboard" use:link>Dashboard</a></li>
        <li><a class="text-white hover:text-gray-300 transition" href="/realtime" use:link>Realtime</a></li>
      </ul>
    </div>
  </nav>
  
  <!-- Global Temperature Alert Banner -->
  {#if temperatureAlert}
    <div class="container mx-auto mt-4">
      <div class="p-3 rounded-md border-l-4 {temperatureAlert.type === 'temperature_high' ? 'bg-red-100 border-red-500' : 'bg-green-100 border-green-500'}">
        <div class="flex">
          <div class="flex-shrink-0">
            {#if temperatureAlert.type === 'temperature_high'}
              <!-- Warning Icon -->
              <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
            {:else}
              <!-- Check Icon -->
              <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            {/if}
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium {temperatureAlert.type === 'temperature_high' ? 'text-red-800' : 'text-green-800'}">
              {temperatureAlert.message}
            </p>
          </div>
          <div class="ml-auto pl-3">
            <div class="-mx-1.5 -my-1.5">
              <button
                on:click={() => temperatureAlert = null}
                class="inline-flex rounded-md p-1.5 {temperatureAlert.type === 'temperature_high' ? 'text-red-500 hover:bg-red-100' : 'text-green-500 hover:bg-green-100'} focus:outline-none"
              >
                <span class="sr-only">Dismiss</span>
                <!-- X Icon -->
                <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  {/if}
  
  <!-- Main Content -->
  <div class="flex-grow container mx-auto p-4 align-items-center">
    <slot></slot>
  </div>
</div>

<style>
</style>
