import axios from 'axios'
import { API_BASE } from '../config'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const verifyNews = (text, maxSources = 5) =>
  api.post('/verify', { text, max_sources: maxSources })

export const getHistory = (limit = 20, offset = 0) =>
  api.get('/history', { params: { limit, offset } })

export const checkHealth = () =>
  api.get('/health')

export default api