<template>
  <div class="detection-image-container">
    <div class="image-wrapper" :style="wrapperStyle">
      <img 
        :src="imageUrl" 
        :alt="alt" 
        ref="image"
        @load="onImageLoad"
        class="detection-image"
      >
      <div v-if="showBoxes && boxes.length" class="boxes-layer">
        <div
          v-for="(box, index) in scaledBoxes"
          :key="index"
          class="bounding-box"
          :style="getBoxStyle(box)"
        >
          <span v-if="showLabels" class="box-label">
            {{ box.label || box.class_id }}: {{ Math.round(box.confidence * 100) }}%
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DetectionImage',
  props: {
    imageUrl: {
      type: String,
      required: true
    },
    boxes: {
      type: Array,
      default: () => []
    },
    alt: {
      type: String,
      default: 'Detection result'
    },
    showLabels: {
      type: Boolean,
      default: true
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
      imageWidth: 0,
      imageHeight: 0,
      scaleX: 1,
      scaleY: 1
    }
  },
  computed: {
    wrapperStyle() {
      return {
        position: 'relative',
        display: 'inline-block',
        maxWidth: '100%'
      }
    },
    scaledBoxes() {
      if (!this.boxes.length || !this.imageWidth || !this.imageHeight) {
        return []
      }

      return this.boxes.map(box => {
        // Предполагаем, что box содержит координаты в формате [x, y, width, height]
        // где x,y - центр или верхний левый угол? В твоем коде это центр
        const [x, y, w, h] = box.box || [box.x, box.y, box.width, box.height]
        
        // Масштабируем координаты
        const scaledX = (x / this.originalWidth) * this.imageWidth
        const scaledY = (y / this.originalHeight) * this.imageHeight
        const scaledW = (w / this.originalWidth) * this.imageWidth
        const scaledH = (h / this.originalHeight) * this.imageHeight

        return {
          ...box,
          x: scaledX,
          y: scaledY,
          width: scaledW,
          height: scaledH
        }
      })
    }
  },
  methods: {
    onImageLoad(event) {
      const img = event.target
      this.imageWidth = img.width
      this.imageHeight = img.height
      this.$emit('loaded', {
        width: this.imageWidth,
        height: this.imageHeight
      })
    },
    getBoxStyle(box) {
      // Предполагаем, что box.x, box.y - координаты верхнего левого угла
      // Если это центр, нужно преобразовать:
      const left = box.x - box.width / 2
      const top = box.y - box.height / 2
      
      return {
        position: 'absolute',
        left: `${left}px`,
        top: `${top}px`,
        width: `${box.width}px`,
        height: `${box.height}px`,
        border: '2px solid #42b983',
        backgroundColor: 'rgba(66, 185, 131, 0.1)',
        pointerEvents: 'none'
      }
    }
  }
}
</script>

<style scoped>
.detection-image-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.image-wrapper {
  position: relative;
  display: inline-block;
  max-width: 100%;
}

.detection-image {
  display: block;
  max-width: 100%;
  height: auto;
}

.boxes-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.bounding-box {
  position: absolute;
  border: 2px solid #42b983;
  background-color: rgba(66, 185, 131, 0.1);
}

.box-label {
  position: absolute;
  top: -20px;
  left: 0;
  background-color: #42b983;
  color: white;
  font-size: 12px;
  padding: 2px 4px;
  border-radius: 2px;
  white-space: nowrap;
}
</style>