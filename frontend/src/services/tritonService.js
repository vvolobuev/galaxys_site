import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class TritonService {
  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      timeout: 30000
    })
  }

  async detectImages(images) {
    try {
      const formData = new FormData()
      
      images.forEach((image) => {
        if (image.file) {
          formData.append('files', image.file)
        } else if (image instanceof File) {
          formData.append('files', image)
        }
      })

      const response = await this.client.post('/api/detect', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      if (response.data && response.data.results) {
        return response.data.results.map(result => ({
          fileName: result.filename,
          detections: result.detections.length,
          boxes: result.detections,
          processedImage: result.image_base64
            ? `data:image/jpeg;base64,${result.image_base64}`
            : null
        }))
      }

      return []
      
    } catch (error) {
      console.error('Error processing images:', error)
      
      if (error.code === 'ECONNABORTED') {
        throw new Error('Connection timeout')
      }
      
      if (error.response) {
        throw new Error(`Server error: ${error.response.status}`)
      } else if (error.request) {
        throw new Error('Backend server not responding')
      } else {
        throw new Error(`Request error: ${error.message}`)
      }
    }
  }

  async getLabeledImages() {
    try {
      const response = await this.client.get('/api/images')
      
      if (response.data && response.data.images) {
        return response.data.images.map(img => ({
          id: img.id,
          url: img.image_base64 ? `data:image/jpeg;base64,${img.image_base64}` : img.url,
          date: img.date || new Date().toLocaleDateString(),
          detections: img.detections ? img.detections.length : 0,
          boxes: img.detections || []
        }))
      }
      
      return []
      
    } catch (error) {
      console.error('Error loading labeled images:', error)
      throw error
    }
  }

  async saveResult(imageData) {
    try {
      const response = await this.client.post('/api/images/save', {
        filename: imageData.filename,
        image_base64: imageData.image_base64,
        detections: imageData.detections,
        date: new Date().toISOString()
      })
      
      return response.data
      
    } catch (error) {
      console.error('Error saving result:', error)
      throw error
    }
  }

  async testConnection() {
    try {
      const response = await this.client.get('/health')
      return { 
        status: 'online', 
        message: 'Backend server available',
        triton: response.data.triton_status
      }
    } catch (error) {
      return { 
        status: 'offline', 
        message: 'Backend server not responding'
      }
    }
  }
}

export default new TritonService()