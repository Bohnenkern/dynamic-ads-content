import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request-Interceptor für Authentifizierung (später)
api.interceptors.request.use(
  (config) => {
    // Hier können später Tokens hinzugefügt werden
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response-Interceptor für Error-Handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// Campaign Generation API
export const generateCampaign = async (campaignData) => {
  const formData = new FormData()
  formData.append('product_image', campaignData.image)
  formData.append('product_description', campaignData.product_description)
  formData.append('campaign_theme', campaignData.campaign_theme)
  formData.append('company_values', JSON.stringify(campaignData.company_values))

  const response = await api.post('/api/v1/campaign/generate', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response.data
}

// Get all users
export const getAllUsers = async () => {
  const response = await api.get('/api/v1/users')
  return response.data
}

// Get user by ID
export const getUserById = async (userId) => {
  const response = await api.get(`/api/v1/users/${userId}`)
  return response.data
}

export default api
