<template>
  <nav class="navigation">
    <div class="nav-container">
      <router-link to="/" class="logo">Galaxy Detection</router-link>
      <div class="nav-right">
        <div class="nav-links">
          <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">
            Загрузить
          </router-link>
          <router-link to="/labeled" class="nav-link" :class="{ active: $route.path === '/labeled' }">
            Размеченные
          </router-link>
        </div>
        <ServerStatus class="server-status-component" />
      </div>
    </div>
  </nav>
</template>

<script>
import ServerStatus from './ServerStatus.vue'

export default {
  name: 'Navigation',
  components: {
    ServerStatus
  }
}
</script>

<style scoped>
.navigation {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.logo {
  color: white;
  text-decoration: none;
  font-size: 1.5rem;
  font-weight: bold;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.nav-links {
  display: flex;
  gap: 1rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s;
  white-space: nowrap;
}

.nav-link:hover {
  background-color: #34495e;
}

.nav-link.active {
  background-color: #42b983;
}

.server-status-component {
  min-width: 160px;
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .nav-right {
    flex-direction: column;
    gap: 1rem;
  }
  
  .nav-links {
    justify-content: center;
  }
  
  .server-status-component {
    align-self: center;
  }
}
</style>