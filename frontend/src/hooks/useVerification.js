import { useState } from 'react'
import { verifyNews } from '../services/api'

export const useVerification = () => {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const verify = async (text, maxSources = 5) => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await verifyNews(text, maxSources)
      setResult(data)
      return data
    } catch (err) {
      const message = err?.response?.data?.detail || 'Cannot connect to server. Please try again.'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { result, loading, error, verify, setResult }
}