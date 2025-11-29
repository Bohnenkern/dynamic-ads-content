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

export default api
