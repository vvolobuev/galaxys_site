<template>
  <div class="labeled">
    <h1>Размеченные изображения</h1>
    
    <div class="filters" v-if="labeledImages.length > 0">
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Поиск по дате..."
          class="search-input"
        >
        <span class="search-icon">🔍</span>
      </div>
      
      <select v-model="sortBy" class="sort-select">
        <option value="dateDesc">📅 Сначала новые</option>
        <option value="dateAsc">📅 Сначала старые</option>
        <option value="detectionsDesc">🎯 Больше объектов</option>
        <option value="detectionsAsc">🎯 Меньше объектов</option>
      </select>
      
      <button @click="clearAllImages" class="btn-clear" title="Очистить все">
        🗑️
      </button>
    </div>
    
    <div v-if="filteredImages.length > 0" class="gallery">
      <div class="image-grid">
        <div 
          v-for="(image, index) in filteredImages" 
          :key="index" 
          class="image-card"
          @click="openModal(image)"
        >
          <img :src="image.url" :alt="'Labeled ' + index">
          <div class="image-overlay">
            <span class="image-date">📅 {{ image.date }}</span>
            <span class="image-detections">🎯 {{ image.detections }}</span>
          </div>
          <button @click.stop="removeImage(image)" class="delete-btn">×</button>
        </div>
      </div>
    </div>
    
    <div v-else-if="!loading" class="empty-state">
      <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
        <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"/>
        <line x1="9" y1="9" x2="15" y2="15"/>
        <line x1="15" y1="9" x2="9" y2="15"/>
      </svg>
      <p>Пока нет размеченных изображений</p>
      <router-link to="/" class="upload-link">📤 Загрузить изображения</router-link>
    </div>

    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Загрузка изображений...</p>
    </div>

    <ImageModal
      :show="modalShow"
      :imageUrl="modalImageUrl"
      :title="modalTitle"
      :boxes="modalBoxes"
      :stats="modalStats"
      :showBoxes="true"
      @close="closeModal"
    />
  </div>
</template>

<script>
import tritonService from '@/services/tritonService'
import ImageModal from '@/components/ImageModal.vue'

export default {
  name: 'LabeledView',
  components: {
    ImageModal
  },
  data() {
    return {
      labeledImages: [],
      loading: false,
      searchQuery: '',
      sortBy: 'dateDesc',
      modalShow: false,
      modalImageUrl: '',
      modalTitle: '',
      modalBoxes: [],
      modalStats: null,
      deleting: false // флаг для предотвращения множественных удалений
    }
  },
  computed: {
    filteredImages() {
      let filtered = this.labeledImages

      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(img => 
          img.date.toLowerCase().includes(query)
        )
      }

      return filtered.sort((a, b) => {
        switch (this.sortBy) {
          case 'dateDesc':
            return new Date(b.date) - new Date(a.date)
          case 'dateAsc':
            return new Date(a.date) - new Date(b.date)
          case 'detectionsDesc':
            return b.detections - a.detections
          case 'detectionsAsc':
            return a.detections - b.detections
          default:
            return 0
        }
      })
    }
  },
  mounted() {
    this.loadLabeledImages()
  },
  methods: {
    async loadLabeledImages() {
      this.loading = true
      try {
        this.labeledImages = await tritonService.getLabeledImages()
      } catch (error) {
        console.error('Failed to load labeled images:', error)
        alert('Ошибка при загрузке изображений')
      } finally {
        this.loading = false
      }
    },
    
    async removeImage(image) {
      if (this.deleting) return // предотвращаем двойное нажатие
      
      if (confirm('Удалить это изображение?')) {
        this.deleting = true
        
        try {
          // Отправляем запрос на удаление на сервер
          await tritonService.deleteImage(image.filename)
          
          // Если успешно, удаляем из локального массива
          this.labeledImages = this.labeledImages.filter(img => img.id !== image.id)
          
        } catch (error) {
          console.error('Error deleting image:', error)
          alert('Ошибка при удалении изображения')
        } finally {
          this.deleting = false
        }
      }
    },
    
    async clearAllImages() {
      if (this.deleting) return
      
      if (confirm('Удалить все размеченные изображения? Это действие нельзя отменить!')) {
        this.deleting = true
        
        try {
          // Отправляем запрос на удаление всех изображений
          const result = await tritonService.deleteAllImages()
          
          // Очищаем локальный массив
          this.labeledImages = []
          
          // Показываем сообщение о результате
          alert(`Удалено ${result.deleted_images} изображений и ${result.deleted_metadata} файлов метаданных`)
          
        } catch (error) {
          console.error('Error deleting all images:', error)
          alert('Ошибка при удалении всех изображений')
        } finally {
          this.deleting = false
        }
      }
    },
    
    openModal(image) {
      this.modalImageUrl = image.url
      this.modalTitle = `Изображение от ${image.date}`
      this.modalBoxes = image.boxes || []
      this.modalStats = {
        width: 'Оригинал',
        height: 'Оригинал',
        date: image.date,
        detections: image.detections
      }
      this.modalShow = true
    },
    
    closeModal() {
      this.modalShow = false
    }
  }
}
</script>

<style scoped>
/* Стили остаются без изменений */
.labeled {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  position: relative;
  min-height: 400px;
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 2rem;
  font-size: 2.2rem;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  justify-content: center;
  flex-wrap: wrap;
  align-items: center;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.25);
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

.sort-select {
  padding: 0.75rem 1rem;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  font-size: 1rem;
  background-color: white;
  cursor: pointer;
  transition: all 0.3s;
  min-width: 180px;
}

.sort-select:focus {
  outline: none;
  border-color: #42b983;
}

.btn-clear {
  padding: 0.75rem 1rem;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  background-color: white;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.3s;
}

.btn-clear:hover {
  border-color: #dc3545;
  background-color: #dc3545;
  color: white;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.image-card {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transition: all 0.3s;
  background-color: #fff;
  cursor: pointer;
  aspect-ratio: 4/3;
}

.image-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}

.image-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.image-card:hover img {
  transform: scale(1.1);
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0,0,0,0.8));
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transform: translateY(100%);
  transition: transform 0.3s;
}

.image-card:hover .image-overlay {
  transform: translateY(0);
}

.image-date,
.image-detections {
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.delete-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: rgba(220, 53, 69, 0.9);
  color: white;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.3s;
  z-index: 10;
}

.image-card:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  transform: scale(1.1);
  background-color: #dc3545;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background-color: #f8f9fa;
  border-radius: 16px;
  color: #6c757d;
}

.empty-state svg {
  color: #42b983;
  margin-bottom: 1.5rem;
}

.empty-state p {
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
}

.upload-link {
  display: inline-block;
  padding: 1rem 2rem;
  background-color: #42b983;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s;
  font-weight: 500;
}

.upload-link:hover {
  background-color: #3aa876;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.3);
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #42b983;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .labeled {
    padding: 1rem;
  }
  
  h1 {
    font-size: 1.8rem;
  }
  
  .filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    max-width: none;
  }
  
  .sort-select,
  .btn-clear {
    width: 100%;
  }
  
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
  }
}
</style>