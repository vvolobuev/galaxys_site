<template>
  <div class="home">
    <h1>Загрузите изображения для детекции</h1>
    
    <div class="upload-section">
      <FileUploader
        ref="uploader"
        :multiple="true"
        accept="image/*"
        :maxSize="20 * 2048 * 2048"
        :maxFiles="1000"
        @files-changed="onFilesChanged"
        @upload="processImages"
        @error="onUploadError"
      >
        <template #icon>
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
        </template>
        
        <template #text>
          <p>Перетащите изображения сюда или нажмите для выбора</p>
          <p class="hint">Поддерживаются форматы: JPG, PNG, WebP (макс. 20 МБ)</p>
        </template>
      </FileUploader>
    </div>

    <div v-if="processedImages.length > 0" class="results-section">
      <h2>Результаты детекции</h2>
      <div class="image-grid">
        <div v-for="(image, index) in processedImages" :key="index" class="image-card result-card" @click="openModal(image)">
          <img :src="image.resultUrl" class="result-image">
          <div class="image-info">
            <p>Найдено объектов: {{ image.detections }}</p>
            <p class="image-date">{{ image.date }}</p>
          </div>
        </div>
      </div>
      
      <div class="results-actions">
        <button @click="clearResults" class="btn btn-secondary">Очистить результаты</button>
        <button @click="saveResults" class="btn btn-primary">Сохранить в размеченные</button>
      </div>
    </div>

    <div v-if="isProcessing" class="loading-overlay">
      <div class="spinner"></div>
      <p>Обработка изображений...</p>
      <p class="processing-hint" v-if="processingProgress > 0">
        Обработано: {{ processingProgress }}%
      </p>
    </div>

    <ImageModal
      :show="modalShow"
      :imageUrl="modalImageUrl"
      :title="modalTitle"
      :boxes="modalBoxes"
      :stats="modalStats"
      @close="closeModal"
    />
  </div>
</template>

<script>
import tritonService from '@/services/tritonService'
import DetectionImage from '@/components/DetectionImage.vue'
import ImageModal from '@/components/ImageModal.vue'
import FileUploader from '@/components/FileUploader.vue'

export default {
  name: 'HomeView',
  components: {
    DetectionImage,
    ImageModal,
    FileUploader
  },
  data() {
    return {
      uploadedFiles: [],
      processedImages: [],
      isProcessing: false,
      processingProgress: 0,
      modalShow: false,
      modalImageUrl: '',
      modalTitle: '',
      modalBoxes: [],
      modalStats: null
    }
  },
  methods: {
    onFilesChanged(files) {
      this.uploadedFiles = files
    },
    onUploadError(error) {
      let message = 'Ошибка загрузки'
      switch (error.type) {
        case 'type':
          message = `Файл ${error.file.name} должен быть изображением`
          break
        case 'size':
          message = error.message
          break
        case 'maxFiles':
          message = error.message
          break
      }
      alert(message)
    },
    async processImages(files) {
      if (!files || files.length === 0) {
        alert('Выберите изображения для обработки')
        return
      }

      this.isProcessing = true
      this.processingProgress = 0
      
      try {
        const progressInterval = setInterval(() => {
          if (this.processingProgress < 90) {
            this.processingProgress += 10
          }
        }, 200)

        const results = await tritonService.detectImages(files)
        
        clearInterval(progressInterval)
        this.processingProgress = 100
        
        setTimeout(() => {
          this.processedImages = results.map(result => ({
            resultUrl: result.processedImage,
            detections: result.detections,
            boxes: result.boxes,
            name: result.fileName,
            date: new Date().toLocaleString()
          }))
          
          this.isProcessing = false
          this.processingProgress = 0
          
          if (this.$refs.uploader) {
            this.$refs.uploader.clearFiles()
          }
        }, 500)
        
      } catch (error) {
        console.error('Error processing images:', error)
        alert('Ошибка при обработке изображений')
        this.isProcessing = false
        this.processingProgress = 0
      }
    },
    openModal(image) {
      this.modalImageUrl = image.resultUrl
      this.modalTitle = image.name || 'Результат детекции'
      this.modalBoxes = image.boxes || []
      this.modalStats = {
        detections: image.detections,
        date: image.date,
        width: 'Оригинал',
        height: 'Оригинал'
      }
      this.modalShow = true
    },
    closeModal() {
      this.modalShow = false
    },
    clearResults() {
      this.processedImages = []
    },
    saveResults() {
      const saved = JSON.parse(localStorage.getItem('labeledImages') || '[]')
      const newImages = this.processedImages.map(img => ({
        url: img.resultUrl,
        date: img.date,
        detections: img.detections,
        boxes: img.boxes,
        width: 'Оригинал',
        height: 'Оригинал'
      }))
      
      localStorage.setItem('labeledImages', JSON.stringify([...newImages, ...saved]))
      alert('Результаты сохранены в раздел "Размеченные"')
    }
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  position: relative;
  min-height: 500px;
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 2rem;
}

.upload-section {
  margin-bottom: 3rem;
}

.results-section {
  margin-top: 3rem;
}

h2 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.image-card {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  background-color: #fff;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.image-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.result-card {
  border: 2px solid transparent;
}

.result-card:hover {
  border-color: #42b983;
}

.image-info {
  padding: 1rem;
  background-color: #fff;
  text-align: center;
}

.image-info p {
  margin: 0.25rem 0;
  color: #2c3e50;
  font-weight: bold;
}

.image-date {
  font-size: 0.85rem;
  color: #6c757d !important;
  font-weight: normal !important;
}

.results-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

.btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #42b983;
  color: white;
}

.btn-primary:hover {
  background-color: #3aa876;
  transform: translateY(-2px);
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
  transform: translateY(-2px);
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.95);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  animation: fadeIn 0.3s;
}

.spinner {
  width: 60px;
  height: 60px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #42b983;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1.5rem;
}

.processing-hint {
  margin-top: 1rem;
  color: #42b983;
  font-size: 1.1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@media (max-width: 768px) {
  .home {
    padding: 1rem;
  }
  
  h1 {
    font-size: 1.5rem;
  }
  
  .results-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>