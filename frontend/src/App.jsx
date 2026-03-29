import { useState } from 'react'
import InputForm from './components/InputForm'
import ResultCard from './components/ResultCard'
import SourceList from './components/SourceList'
import ConfidenceMeter from './components/ConfidenceMeter'
import HistoryList from './components/HistoryList'
import { useVerification } from './hooks/useVerification'
import { useHistory } from './hooks/useHistory'

export default function App() {
  const { result, loading, error, verify, setResult } = useVerification()
  const { history, fetchHistory } = useHistory()
  const [localError, setLocalError] = useState(null)

  const handleSubmit = async (text) => {
    setLocalError(null)
    try {
      const data = await verify(text, 5)
      setResult(data)
      fetchHistory(0)
    } catch (err) {
      const status = err?.response?.status
      if (status === 429) {
        setLocalError('Too many requests. Please wait 1 minute.')
      } else if (status === 422) {
        setLocalError(err?.response?.data?.detail || 'Input validation error.')
      } else {
        setLocalError('Something went wrong. Please refresh.')
      }
    }
  }

  return (
    <div className="app">
      <header className="hero">
        <div>
          <h1>AI News Verification</h1>
          <p>Submit a headline and get real-time verification with source attribution.</p>
        </div>
        <div className="hero-badge">Live Source Check</div>
      </header>

      <main className="grid">
        <section>
          <InputForm onSubmit={handleSubmit} isLoading={loading} />
          {(error || localError) && <p className="error">{localError || error}</p>}
          <ResultCard result={result} />
        </section>

        <aside>
          <ConfidenceMeter value={result?.confidence || 0} />
          <SourceList sources={result?.sources || []} />
          <HistoryList items={history} />
        </aside>
      </main>
    </div>
  )
}