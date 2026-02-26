<template>
  <div class="statistics">
    <div class="stats-header">
      <h3>📊 Статистика</h3>
      <button @click="$emit('close')" class="close-btn">×</button>
    </div>
    
    <div class="stats-content">
      <div class="stat-item">
        <div class="stat-icon">📸</div>
        <div class="stat-info">
          <span class="stat-label">Всего изображений</span>
          <span class="stat-value">{{ stats.totalImages }}</span>
        </div>
      </div>
      
      <div class="stat-item">
        <div class="stat-icon">🎯</div>
        <div class="stat-info">
          <span class="stat-label">Всего объектов</span>
          <span class="stat-value">{{ stats.totalDetections }}</span>
        </div>
      </div>
      
      <div class="stat-item">
        <div class="stat-icon">📅</div>
        <div class="stat-info">
          <span class="stat-label">Сред. объектов на изображение</span>
          <span class="stat-value">{{ avgDetectionsPerImage }}</span>
        </div>
      </div>
      
      <div class="stat-item">
        <div class="stat-icon">🔥</div>
        <div class="stat-info">
          <span class="stat-label">Макс. объектов</span>
          <span class="stat-value">{{ stats.maxDetections }}</span>
        </div>
      </div>
    </div>
    
    <div v-if="classStats.length > 0" class="class-stats">
      <h4>Распределение по классам</h4>
      <div class="class-list">
        <div v-for="stat in classStats" :key="stat.class" class="class-item">
          <span class="class-name">{{ stat.class }}</span>
          <div class="class-bar">
            <div 
              class="class-bar-fill" 
              :style="{ width: (stat.count / stats.totalDetections * 100) + '%' }"
            ></div>
          </div>
          <span class="class-count">{{ stat.count }}</span>
        </div>
      </div>
    </div>
    
    <div class="stats-footer">
      <p class="last-update">Последнее обновление: {{ lastUpdate }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Statistics',
  props: {
    images: {
      type: Array,
      required: true
    }
  },
  emits: ['close'],
  data() {
    return {
      lastUpdate: new Date().toLocaleString()
    }
  },
  computed: {
    stats() {
      const totalImages = this.images.length
      let totalDetections = 0
      let maxDetections = 0
      const classCount = {}
      
      this.images.forEach(image => {
        totalDetections += image.detections || 0
        maxDetections = Math.max(maxDetections, image.detections || 0)
        
        // Подсчет по классам
        if (image.boxes) {
          image.boxes.forEach(box => {
            const className = box.label || `class_${box.class_id}`
            classCount[className] = (classCount[className] || 0) + 1
          })
        }
      })
      
      return {
        totalImages,
        totalDetections,
        maxDetections,
        classCount
      }
    },
    avgDetectionsPerImage() {
      if (this.stats.totalImages === 0) return 0
      return (this.stats.totalDetections / this.stats.totalImages).toFixed(1)
    },
    classStats() {
      return Object.entries(this.stats.classCount)
        .map(([className, count]) => ({ class: className, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10) // Топ-10 классов
    }
  }
}
</script>

<style scoped>
.statistics {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 400px;
  max-width: 90vw;
  max-height: 80vh;
  overflow-y: auto;
  animation: slideIn 0.3s;
}

.stats-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f8f9fa;
  border-radius: 12px 12px 0 0;
}

.stats-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
  padding: 0 0.5rem;
  transition: color 0.3s;
}

.close-btn:hover {
  color: #dc3545;
}

.stats-content {
  padding: 1.5rem;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  transition: transform 0.3s;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 2rem;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.85rem;
  color: #6c757d;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #42b983;
}

.class-stats {
  padding: 1.5rem;
  border-top: 1px solid #dee2e6;
}

.class-stats h4 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
}

.class-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.class-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.class-name {
  width: 100px;
  font-size: 0.9rem;
  color: #495057;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.class-bar {
  flex: 1;
  height: 8px;
  background-color: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.class-bar-fill {
  height: 100%;
  background-color: #42b983;
  border-radius: 4px;
  transition: width 0.3s;
}

.class-count {
  min-width: 40px;
  text-align: right;
  font-size: 0.9rem;
  color: #6c757d;
}

.stats-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #dee2e6;
  background-color: #f8f9fa;
  border-radius: 0 0 12px 12px;
}

.last-update {
  margin: 0;
  font-size: 0.85rem;
  color: #6c757d;
  text-align: center;
}

@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .stats-content {
    grid-template-columns: 1fr;
  }
  
  .class-name {
    width: 80px;
  }
}
</style>