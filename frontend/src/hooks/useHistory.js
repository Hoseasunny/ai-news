import { useEffect, useState } from 'react'
import { getHistory } from '../services/api'

export const useHistory = (limit = 20) => {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchHistory = async (offset = 0) => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await getHistory(limit, offset)
      setHistory(data.items)
    } catch (err) {
      setError('Cannot connect to server. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHistory(0)
  }, [])

  return { history, loading, error, fetchHistory }
}