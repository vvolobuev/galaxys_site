<template>
  <div class="server-status" :class="statusClass">
    <div class="status-indicator" :class="statusClass"></div>
    <span class="status-text">{{ statusText }}</span>
    <button v-if="showRetry && status === 'offline'" @click="checkConnection" class="retry-btn">
      ⟲
    </button>
  </div>
</template>

<script>
import tritonService from '@/services/tritonService'

export default {
  name: 'ServerStatus',
  props: {
    showRetry: {
      type: Boolean,
      default: true
    },
    checkInterval: {
      type: Number,
      default: 30000 // 30 секунд
    }
  },
  data() {
    return {
      status: 'checking',
      statusText: 'Проверка соединения...'
    }
  },
  computed: {
    statusClass() {
      return {
        'status-online': this.status === 'online',
        'status-offline': this.status === 'offline',
        'status-checking': this.status === 'checking'
      }
    }
  },
  mounted() {
    this.checkConnection()
    if (this.checkInterval > 0) {
      this.interval = setInterval(this.checkConnection, this.checkInterval)
    }
  },
  beforeUnmount() {
    if (this.interval) {
      clearInterval(this.interval)
    }
  },
  methods: {
    async checkConnection() {
      this.status = 'checking'
      this.statusText = 'Проверка соединения...'
      
      try {
        const result = await tritonService.testConnection()
        if (result.status === 'ok' || result.status === 'online') {
          this.status = 'online'
          this.statusText = 'Сервер доступен'
        } else {
          this.status = 'offline'
          this.statusText = 'Сервер недоступен'
        }
      } catch (error) {
        this.status = 'offline'
        this.statusText = 'Сервер недоступен'
      }
    }
  }
}
</script>

<style scoped>
.server-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-indicator.status-online {
  background-color: #42b983;
  box-shadow: 0 0 8px rgba(66, 185, 131, 0.5);
  animation: pulse 2s infinite;
}

.status-indicator.status-offline {
  background-color: #dc3545;
}

.status-indicator.status-checking {
  background-color: #ffc107;
  animation: blink 1s infinite;
}

.status-text {
  color: #495057;
}

.retry-btn {
  background: none;
  border: none;
  color: #6c757d;
  font-size: 16px;
  cursor: pointer;
  padding: 0 4px;
  transition: transform 0.3s;
}

.retry-btn:hover {
  transform: rotate(180deg);
  color: #42b983;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(66, 185, 131, 0.7);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(66, 185, 131, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(66, 185, 131, 0);
  }
}

@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0.4; }
  100% { opacity: 1; }
}
</style>