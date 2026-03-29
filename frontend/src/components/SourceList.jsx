import { useState } from 'react'

const scoreColor = (score) => {
  if (score >= 0.85) return 'good'
  if (score >= 0.7) return 'mid'
  return 'low'
}

const formatDate = (value) => {
  if (!value) return 'Unknown date'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Unknown date'
  return date.toLocaleDateString()
}

const getDomain = (url) => {
  try {
    return new URL(url).hostname.replace('www.', '')
  } catch {
    return 'unknown'
  }
}

export default function SourceList({ sources = [] }) {
  const [showAll, setShowAll] = useState(false)
  const visible = showAll ? sources : sources.slice(0, 5)

  if (!sources.length) {
    return (
      <div className="card">
        <h3>Sources</h3>
        <p className="muted">No sources available for this query.</p>
      </div>
    )
  }

  return (
    <div className="card">
      <h3>Sources</h3>
      <div className="source-list">
        {visible.map((s, idx) => (
          <div className="source-item" key={`${s.url}-${idx}`}>
            <a href={s.url} target="_blank" rel="noreferrer">
              {s.title}
            </a>
            <div className="source-meta">
              <span className="pill">{getDomain(s.url)}</span>
              <span className={`pill ${scoreColor(s.credibility_score)}`}>
                Credibility {Math.round((s.credibility_score || 0) * 100)}%
              </span>
              <span className="pill">
                Similarity {Math.round((s.similarity_score || 0) * 100)}%
              </span>
              <span className="pill">{formatDate(s.published_at)}</span>
            </div>
          </div>
        ))}
      </div>
      {sources.length > 5 && (
        <button className="ghost" onClick={() => setShowAll(!showAll)}>
          {showAll ? 'Show less' : 'Show more'}
        </button>
      )}
    </div>
  )
}