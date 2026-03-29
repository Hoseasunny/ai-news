export default function HistoryList({ items = [] }) {
  return (
    <div className="card">
      <h3>Recent Verifications</h3>
      {!items.length && <p className="muted">No history yet.</p>}
      <ul className="history-list">
        {items.map((item) => (
          <li key={item.query_id}>
            <span className={`dot ${item.status}`} />
            <div>
              <div className="history-text">{item.input_preview}</div>
              <div className="history-meta">
                {item.status} • {Math.round((item.confidence || 0) * 100)}% • {new Date(item.created_at).toLocaleString()}
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}