<template>
  <Teleport to="body">
    <div v-if="show" class="modal-overlay" @click.self="close">
      <div class="modal-container" :class="{ 'modal-fullscreen': fullscreen }">
        <div class="modal-header">
          <h3>{{ title }}</h3>
          <div class="modal-actions">
            <button @click="toggleFullscreen" class="modal-action-btn">
              <svg v-if="!fullscreen" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/>
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 14h6v6M20 10h-6V4M14 10l7-7M3 21l7-7"/>
              </svg>
            </button>
            <button @click="downloadImage" class="modal-action-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
            </button>
            <button @click="close" class="modal-action-btn close-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>
        <div class="modal-body">
          <div class="image-wrapper">
            <img :src="imageUrl" :alt="title" class="modal-image">
            <div v-if="showBoxes && boxes.length" class="boxes-overlay">
              <div
                v-for="(box, index) in scaledBoxes"
                :key="index"
                class="modal-bounding-box"
                :style="getBoxStyle(box)"
              >
                <span class="modal-box-label">
                  {{ box.label || box.class_id }}: {{ Math.round(box.confidence * 100) }}%
                </span>
              </div>
            </div>
          </div>
        </div>
        <div v-if="stats" class="modal-footer">
          <div class="image-stats">
            <span>Размер: {{ stats.width }} x {{ stats.height }}</span>
            <span>Объектов: {{ boxes.length }}</span>
            <span v-if="stats.date">Дата: {{ stats.date }}</span>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
export default {
  name: 'ImageModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    imageUrl: {
      type: String,
      required: true
    },
    title: {
      type: String,
      default: 'Просмотр изображения'
    },
    boxes: {
      type: Array,
      default: () => []
    },
    stats: {
      type: Object,
      default: null
    },
    showBoxes: {
      type: Boolean,
      default: true
    },
    originalWidth: {
      type: Number,
      default: 640
    },
    originalHeight: {
      type: Number,
      default: 640
    }
  },
  data() {
    return {
      fullscreen: false,
      imageWidth: 0,
      imageHeight: 0
    }
  },
  computed: {
    scaledBoxes() {
      if (!this.boxes.length || !this.imageWidth || !this.imageHeight) {
        return []
      }

      return this.boxes.map(box => {
        const [x, y, w, h] = box.box || [box.x, box.y, box.width, box.height]
        
        const scaleX = this.imageWidth / this.originalWidth
        const scaleY = this.imageHeight / this.originalHeight
        
        return {
          ...box,
          x: x * scaleX,
          y: y * scaleY,
          width: w * scaleX,
          height: h * scaleY
        }
      })
    }
  },
  methods: {
    close() {
      this.$emit('close')
    },
    toggleFullscreen() {
      this.fullscreen = !this.fullscreen
    },
    downloadImage() {
      const link = document.createElement('a')
      link.href = this.imageUrl
      link.download = `detection-${Date.now()}.jpg`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },
    onImageLoad(event) {
      const img = event.target
      this.imageWidth = img.width
      this.imageHeight = img.height
    },
    getBoxStyle(box) {
      const left = box.x - box.width / 2
      const top = box.y - box.height / 2
      
      return {
        left: `${left}px`,
        top: `${top}px`,
        width: `${box.width}px`,
        height: `${box.height}px`
      }
    }
  },
  watch: {
    show(newVal) {
      if (newVal) {
        document.body.style.overflow = 'hidden'
      } else {
        document.body.style.overflow = ''
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  animation: fadeIn 0.3s;
}

.modal-container {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 1200px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  animation: slideIn 0.3s;
  overflow: hidden;
}

.modal-container.modal-fullscreen {
  width: 100vw;
  height: 100vh;
  max-width: none;
  max-height: none;
  border-radius: 0;
}

.modal-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f8f9fa;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.modal-actions {
  display: flex;
  gap: 0.5rem;
}

.modal-action-btn {
  background: none;
  border: none;
  padding: 0.5rem;
  cursor: pointer;
  border-radius: 4px;
  color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.modal-action-btn:hover {
  background-color: #e9ecef;
  color: #42b983;
}

.close-btn:hover {
  color: #dc3545;
}

.modal-body {
  flex: 1;
  overflow: auto;
  padding: 1.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
}

.image-wrapper {
  position: relative;
  display: inline-block;
  max-width: 100%;
}

.modal-image {
  display: block;
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.modal-fullscreen .modal-image {
  max-height: calc(100vh - 120px);
}

.boxes-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.modal-bounding-box {
  position: absolute;
  border: 2px solid #42b983;
  background-color: rgba(66, 185, 131, 0.1);
  pointer-events: none;
}

.modal-box-label {
  position: absolute;
  top: -24px;
  left: 0;
  background-color: #42b983;
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 2px;
  white-space: nowrap;
  pointer-events: none;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

.image-stats {
  display: flex;
  gap: 2rem;
  justify-content: center;
  color: #6c757d;
  font-size: 0.9rem;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from {
    transform: translateY(-30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .modal-container {
    width: 95%;
    max-height: 95vh;
  }
  
  .image-stats {
    flex-direction: column;
    gap: 0.5rem;
    align-items: center;
  }
}
</style>