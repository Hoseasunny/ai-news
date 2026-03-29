export default function ConfidenceMeter({ value = 0 }) {
  const pct = Math.round(value * 100)
  return (
    <div className="card">
      <h3>Confidence Meter</h3>
      <div className="meter">
        <div className="meter-fill" style={{ width: `${pct}%` }} />
      </div>
      <p className="muted">Overall confidence: {pct}%</p>
    </div>
  )
}