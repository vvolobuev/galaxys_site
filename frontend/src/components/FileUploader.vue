<template>
  <div class="file-uploader">
    <div 
      class="upload-area"
      :class="{ 'drag-over': isDragging }"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop"
      @click="triggerFileInput"
    >
      <input
        type="file"
        ref="fileInput"
        :multiple="multiple"
        :accept="accept"
        @change="onFileSelect"
        style="display: none"
      >
      
      <div class="upload-content">
        <slot name="icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
        </slot>
        
        <slot name="text">
          <p>{{ dragText }}</p>
          <p class="hint" v-if="hint">{{ hint }}</p>
        </slot>
      </div>
    </div>

    <div v-if="files.length > 0" class="file-list">
      <div v-for="(file, index) in files" :key="index" class="file-item">
        <div class="file-info">
          <span class="file-name">{{ file.name }}</span>
          <span class="file-size">{{ formatFileSize(file.size) }}</span>
        </div>
        
        <div class="file-progress" v-if="showProgress">
          <div class="progress-bar" :style="{ width: file.progress + '%' }"></div>
          <span class="progress-text">{{ file.progress }}%</span>
        </div>
        
        <div class="file-actions">
          <button 
            v-if="removable" 
            @click.stop="removeFile(index)"
            class="file-action-btn remove"
            title="Удалить"
          >
            ×
          </button>
          <button 
            v-if="file.preview && previewable" 
            @click.stop="previewFile(file)"
            class="file-action-btn preview"
            title="Предпросмотр"
          >
            👁
          </button>
        </div>
      </div>
    </div>

    <div v-if="files.length > 0 && showActions" class="upload-actions">
      <slot name="actions" :files="files" :clear="clearFiles">
        <button @click="clearFiles" class="btn btn-secondary">Очистить</button>
        <button @click="$emit('upload', files)" class="btn btn-primary">Загрузить</button>
      </slot>
    </div>

    <ImageModal
      :show="previewShow"
      :imageUrl="previewUrl"
      :title="previewTitle"
      @close="closePreview"
    />
  </div>
</template>

<script>
import ImageModal from './ImageModal.vue'

export default {
  name: 'FileUploader',
  components: {
    ImageModal
  },
  props: {
    multiple: {
      type: Boolean,
      default: true
    },
    accept: {
      type: String,
      default: 'image/*'
    },
    dragText: {
      type: String,
      default: 'Перетащите файлы сюда или нажмите для выбора'
    },
    hint: {
      type: String,
      default: ''
    },
    removable: {
      type: Boolean,
      default: true
    },
    previewable: {
      type: Boolean,
      default: true
    },
    showProgress: {
      type: Boolean,
      default: false
    },
    showActions: {
      type: Boolean,
      default: true
    },
    maxSize: {
      type: Number,
      default: 10 * 1024 * 1024 // 10MB
    },
    maxFiles: {
      type: Number,
      default: 10
    }
  },
  emits: ['files-changed', 'upload', 'error'],
  data() {
    return {
      isDragging: false,
      files: [],
      previewShow: false,
      previewUrl: '',
      previewTitle: ''
    }
  },
  methods: {
    onDragOver() {
      this.isDragging = true
    },
    onDragLeave() {
      this.isDragging = false
    },
    onDrop(event) {
      this.isDragging = false
      const droppedFiles = Array.from(event.dataTransfer.files)
      this.addFiles(droppedFiles)
    },
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    onFileSelect(event) {
      const selectedFiles = Array.from(event.target.files)
      this.addFiles(selectedFiles)
      this.$refs.fileInput.value = '' // Сброс input для возможности выбора того же файла
    },
    addFiles(newFiles) {
      // Фильтрация по типу
      const validFiles = newFiles.filter(file => {
        if (!file.type.startsWith('image/')) {
          this.$emit('error', { type: 'type', file, message: 'Файл должен быть изображением' })
          return false
        }
        return true
      })

      // Фильтрация по размеру
      const sizeValidFiles = validFiles.filter(file => {
        if (file.size > this.maxSize) {
          this.$emit('error', { 
            type: 'size', 
            file, 
            message: `Файл слишком большой. Максимальный размер: ${this.formatFileSize(this.maxSize)}` 
          })
          return false
        }
        return true
      })

      // Проверка количества файлов
      if (!this.multiple && sizeValidFiles.length > 0) {
        this.files = [sizeValidFiles[0]]
      } else {
        const totalFiles = this.files.length + sizeValidFiles.length
        if (totalFiles > this.maxFiles) {
          this.$emit('error', { 
            type: 'maxFiles', 
            message: `Максимальное количество файлов: ${this.maxFiles}` 
          })
          return
        }
        this.files = [...this.files, ...sizeValidFiles.slice(0, this.maxFiles - this.files.length)]
      }

      // Создание превью для изображений
      this.files.forEach(file => {
        if (!file.preview && file.type.startsWith('image/')) {
          const reader = new FileReader()
          reader.onload = (e) => {
            file.preview = e.target.result
            this.$emit('files-changed', this.files)
          }
          reader.readAsDataURL(file)
        }
      })

      this.$emit('files-changed', this.files)
    },
    removeFile(index) {
      this.files.splice(index, 1)
      this.$emit('files-changed', this.files)
    },
    clearFiles() {
      this.files = []
      this.$emit('files-changed', this.files)
    },
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    previewFile(file) {
      if (file.preview) {
        this.previewUrl = file.preview
        this.previewTitle = file.name
        this.previewShow = true
      }
    },
    closePreview() {
      this.previewShow = false
    },
    updateFileProgress(index, progress) {
      if (this.files[index]) {
        this.files[index].progress = progress
      }
    }
  }
}
</script>

<style scoped>
.file-uploader {
  width: 100%;
}

.upload-area {
  border: 3px dashed #42b983;
  border-radius: 8px;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background-color: #f8f9fa;
}

.upload-area:hover {
  border-color: #2c3e50;
  background-color: #e9ecef;
}

.upload-area.drag-over {
  border-color: #2c3e50;
  background-color: #e9ecef;
  transform: scale(1.02);
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.upload-content svg {
  color: #42b983;
}

.upload-content p {
  margin: 0;
  color: #6c757d;
}

.hint {
  font-size: 0.9rem;
  color: #adb5bd;
}

.file-list {
  margin-top: 1.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  overflow: hidden;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #dee2e6;
  background-color: white;
}

.file-item:last-child {
  border-bottom: none;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.file-name {
  font-weight: 500;
  color: #2c3e50;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 0.85rem;
  color: #6c757d;
}

.file-progress {
  flex: 1;
  margin: 0 1rem;
  position: relative;
  height: 20px;
  background-color: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background-color: #42b983;
  transition: width 0.3s;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 0.75rem;
  font-weight: bold;
  text-shadow: 0 0 2px rgba(0,0,0,0.5);
}

.file-actions {
  display: flex;
  gap: 0.5rem;
}

.file-action-btn {
  background: none;
  border: none;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  border-radius: 4px;
  font-size: 1.2rem;
  transition: all 0.3s;
}

.file-action-btn.remove:hover {
  background-color: #dc3545;
  color: white;
}

.file-action-btn.preview:hover {
  background-color: #42b983;
  color: white;
}

.upload-actions {
  margin-top: 1rem;
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn {
  padding: 0.75rem 1.5rem;
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
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

@media (max-width: 768px) {
  .file-item {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .file-progress {
    margin: 0.5rem 0;
  }
  
  .upload-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>