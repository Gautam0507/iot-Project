<script>
  import { onMount, onDestroy } from 'svelte';
  import { sensorData, sensorMetadata } from '../stores/sensorStore.js';
  import Chart from 'chart.js/auto';
  
  let charts = {};
  let unsubscribe;
  
  onMount(() => {
    // Create charts for each sensor
    Object.keys(sensorMetadata).forEach(sensorId => {
      const ctx = document.getElementById(`sensor-${sensorId}-chart`).getContext('2d');
      const sensor = sensorMetadata[sensorId];
      
      charts[sensorId] = new Chart(ctx, {
        type: 'line',
        data: {
          labels: [],
          datasets: [{
            label: `${sensor.name} ${sensor.unit}`,
            data: [],
            borderColor: sensorId === '4' ? 'rgb(255, 99, 132)' : 'rgb(75, 192, 192)',
            tension: 0.1,
            pointRadius: sensorId === '4' ? 5 : 2 // Larger points for relay status
          }]
        },
        options: {
          responsive: true,
          scales: {
            x: {
              title: {
                display: true,
                text: 'Time'
              }
            },
            y: {
              title: {
                display: true,
                text: sensor.unit || 'Value'
              },
              // For relay status, limit y axis to 0-1
              ...(sensorId === '4' && {
                min: 0,
                max: 1,
                ticks: {
                  stepSize: 1,
                  callback: function(value) {
                    return value === 0 ? 'OFF' : 'ON';
                  }
                }
              })
            }
          }
        }
      });
    });
    
    // Subscribe to store updates
    unsubscribe = sensorData.subscribe(data => {
      updateCharts(data);
    });
  });
  
  onDestroy(() => {
    if (unsubscribe) unsubscribe();
    
    // Destroy charts to prevent memory leaks
    Object.values(charts).forEach(chart => {
      if (chart) chart.destroy();
    });
  });
  
  function updateCharts(data) {
    Object.entries(data).forEach(([sensorId, values]) => {
      if (charts[sensorId] && values && values.length > 0) {
        charts[sensorId].data.labels = values.map(item => {
          const date = new Date(item.timestamp);
          return date.toLocaleTimeString();
        });
        
        charts[sensorId].data.datasets[0].data = values.map(item => item.value);
        charts[sensorId].update();
      }
    });
  }
</script>

<div class="container mx-auto p-4 width-full">
  <h3 class="text-2xl font-bold mb-6">Dashboard</h3>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    {#each Object.entries(sensorMetadata) as [id, sensor]}
      <div class="bg-white p-4 rounded shadow">
        <h4 class="text-xl mb-3">{sensor.name}</h4>
        <canvas id="sensor-{id}-chart"></canvas>
      </div>
    {/each}
  </div>
</div>
