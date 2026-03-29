const STATUS_COLORS = {
  real: '#22c55e',
  fake: '#ef4444',
  uncertain: '#eab308'
}

export default function ResultCard({ result }) {
  if (!result) return null
  const color = STATUS_COLORS[result.status] || '#94a3b8'
  const confidencePct = Math.round((result.confidence || 0) * 100)

  return (
    <div className="card result-card">
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
      <p className="meta">Processing time: {result.processing_time_ms} ms</p>
    </div>
  )
}