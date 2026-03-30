const colorFor = (pct) => {
  if (pct >= 75) return '#22c55e'
  if (pct >= 45) return '#f59e0b'
  return '#ef4444'
}

export default function ConfidenceMeter({ value = 0, status }) {
  const pct = Math.round(value * 100)
  const stroke = colorFor(pct)
  const radius = 54
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (pct / 100) * circumference

  return (
    <div className="card">
      <h3>Confidence Meter</h3>
      <div className="gauge">
        <svg width="140" height="140" viewBox="0 0 140 140">
          <circle cx="70" cy="70" r={radius} stroke="rgba(148,163,184,0.2)" strokeWidth="12" fill="none" />
          <circle
            cx="70"
            cy="70"
            r={radius}
            stroke={stroke}
            strokeWidth="12"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
          />
        </svg>
        <div className="gauge-center">
          <div className="gauge-value">{pct}%</div>
          <div className="gauge-label">{status || 'confidence'}</div>
        </div>
      </div>
      <p className="muted">Overall confidence</p>
    </div>
  )
}
