<script>
  import { link } from 'svelte-spa-router';
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
  
  <!-- Main Content -->
  <div class="flex-grow container mx-auto p-4 align-items-center">
    <slot></slot>
  </div>
</div>

<style>
</style>

