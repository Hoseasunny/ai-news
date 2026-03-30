import { useEffect, useState } from 'react'
import { getHealthExtended } from '../services/api'

export default function HealthStatus() {
  const [providers, setProviders] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true
    const fetchHealth = async () => {
      try {
        const { data } = await getHealthExtended()
        if (mounted) setProviders(data.providers)
      } catch {
        if (mounted) setError('Unable to check API status')
      }
    }
    fetchHealth()
  }, [])

  return (
    <div className="card">
      <h3>API Status</h3>
      {error && <p className="error">{error}</p>}
      {!error && !providers && <p className="muted">Checking providers...</p>}
      {providers && (
        <div className="status-list">
          {Object.entries(providers).map(([key, value]) => (
            <div key={key} className={`status-pill ${value.startsWith('available') ? 'ok' : value.startsWith('unconfigured') ? 'warn' : 'bad'}`}>
              <span className="status-key">{key}</span>
              <span className="status-val">{value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}