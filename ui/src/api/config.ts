import axios from 'axios'

// Create a custom axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('API Error Response:', error.response.data)
      return Promise.reject(new Error(error.response.data || 'Server error'))
    } else if (error.request) {
      // The request was made but no response was received
      console.error('API Request Error:', error.request)
      return Promise.reject(new Error('No response from server'))
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('API Setup Error:', error.message)
      return Promise.reject(error)
    }
  }
)

export default api
