const STATUS_COLORS = {
  real: '#22c55e',
  fake: '#ef4444',
  uncertain: '#eab308'
}

export default function ResultCard({ result, loading, headline }) {
  if (!result && !loading) return null
  if (loading && !result) {
    return (
      <div className="card result-card">
        <div className="loading">
          <span className="dot" />
          <span className="dot" />
          <span className="dot" />
        </div>
        <p className="muted">Analyzing sources and credibility...</p>
      </div>
    )
  }
  const color = STATUS_COLORS[result.status] || '#94a3b8'
  const confidencePct = Math.round((result.confidence || 0) * 100)

  return (
    <div className="card result-card">
      {headline && <h2 className="headline">{headline}</h2>}
      <div className="status-row">
        <span className="status-badge" style={{ background: color }}>
          {result.status.toUpperCase()}
        </span>
        <span className="confidence">Confidence: {confidencePct}%</span>
      </div>
      <div className="progress">
        <div className="progress-bar" style={{ width: `${confidencePct}%`, background: color }} />
      </div>
      <p className="summary">{result.summary}</p>
      {result.reasons && result.reasons.length > 0 && (
        <ul className="reasons">
          {result.reasons.map((r, i) => (
            <li key={`${r}-${i}`}>{r}</li>
          ))}
        </ul>
      )}
      <p className="meta">Processing time: {result.processing_time_ms} ms</p>
    </div>
  )
}
