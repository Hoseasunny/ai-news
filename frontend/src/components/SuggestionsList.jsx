export default function SuggestionsList({ items = [] }) {
  if (!items.length) return null

  return (
    <div className="card">
      <h3>Similar News Suggestions</h3>
      <div className="source-grid">
        {items.map((s, idx) => (
          <div className="source-card" key={`${s.url}-${idx}`}>
            <div className="source-header">
              <img src={`https://www.google.com/s2/favicons?domain=${s.source}&sz=64`} alt="" />
              <div>
                <a href={s.url} target="_blank" rel="noreferrer">
                  {s.title}
                </a>
                <div className="source-sub">{s.source}</div>
              </div>
            </div>
            <div className="source-meta">
              <span className="pill">Similarity {Math.round((s.similarity_score || 0) * 100)}%</span>
              <span className="pill" title="Credibility score from source_credibility table">
                Credibility {Math.round((s.credibility_score || 0) * 100)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
