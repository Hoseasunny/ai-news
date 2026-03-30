import { useState } from 'react'
import InputForm from './components/InputForm'
import ResultCard from './components/ResultCard'
import SourceList from './components/SourceList'
import ConfidenceMeter from './components/ConfidenceMeter'
import HistoryList from './components/HistoryList'
import HealthStatus from './components/HealthStatus'
import SuggestionsList from './components/SuggestionsList'
import { useVerification } from './hooks/useVerification'
import { useHistory } from './hooks/useHistory'

export default function App() {
  const { result, loading, error, verify, setResult } = useVerification()
  const { history, fetchHistory } = useHistory()
  const [localError, setLocalError] = useState(null)
  const [activeTab, setActiveTab] = useState('sources')
  const [lastInput, setLastInput] = useState('')

  const handleSubmit = async (text) => {
    setLocalError(null)
    try {
      const data = await verify(text, 5)
      setLastInput(text)
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
          <div className="sticky-input">
            <InputForm onSubmit={handleSubmit} isLoading={loading} />
          </div>
          {(error || localError) && <p className="error">{localError || error}</p>}
          <ResultCard result={result} loading={loading} headline={lastInput} />
        </section>

        <aside>
          <ConfidenceMeter value={result?.confidence || 0} status={result?.status} />
          <div className="tabs">
            <button className={activeTab === 'sources' ? 'active' : ''} onClick={() => setActiveTab('sources')}>Sources</button>
            <button className={activeTab === 'similar' ? 'active' : ''} onClick={() => setActiveTab('similar')}>Similar News</button>
            <button className={activeTab === 'history' ? 'active' : ''} onClick={() => setActiveTab('history')}>Timeline</button>
            <button className={activeTab === 'status' ? 'active' : ''} onClick={() => setActiveTab('status')}>API Status</button>
          </div>
          {activeTab === 'sources' && <SourceList sources={result?.sources || []} />}
          {activeTab === 'similar' && <SuggestionsList items={result?.suggestions || []} />}
          {activeTab === 'history' && <HistoryList items={history} />}
          {activeTab === 'status' && <HealthStatus />}
        </aside>
      </main>
    </div>
  )
}
