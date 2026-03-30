export default function HistoryList({ items = [] }) {
  const grouped = items.reduce((acc, item) => {
    const date = new Date(item.created_at).toLocaleDateString()
    acc[date] = acc[date] || []
    acc[date].push(item)
    return acc
  }, {})

  return (
    <div className="card">
      <h3>Recent Verifications</h3>
      {!items.length && <p className="muted">No history yet.</p>}
      <div className="timeline">
        {Object.entries(grouped).map(([date, entries]) => (
          <div className="timeline-group" key={date}>
            <div className="timeline-date">{date}</div>
            <div className="timeline-items">
              {entries.map((item) => (
                <div className="timeline-item" key={item.query_id}>
                  <span className={`dot ${item.status}`} />
                  <div>
                    <div className="history-text">{item.input_preview}</div>
                    <div className="history-meta">
                      {item.status} • {Math.round((item.confidence || 0) * 100)}% • {new Date(item.created_at).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}