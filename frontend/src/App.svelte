<script>
  import Router from 'svelte-spa-router';
  import Dashboard from './routes/Dashboard.svelte';
  import Realtime from './routes/Realtime.svelte';
  import Layout from './components/Layout.svelte';

  // Define routes
  const routes = {
    '/dashboard': Dashboard,
    '/realtime': Realtime,
    '*': Dashboard // Default route
  };
</script>

<Layout>
  <Router {routes} />
</Layout>

