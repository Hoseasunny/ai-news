import { useMemo, useState } from 'react'

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

const thresholds = [
  { label: 'All', value: 0 },
  { label: '70%+', value: 0.7 },
  { label: '85%+', value: 0.85 }
]

export default function SourceList({ sources = [] }) {
  const [showAll, setShowAll] = useState(false)
  const [minCred, setMinCred] = useState(0)
  const filtered = useMemo(
    () => sources.filter((s) => (s.credibility_score || 0) >= minCred),
    [sources, minCred]
  )
  const visible = showAll ? filtered : filtered.slice(0, 6)

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
      <div className="filters">
        {thresholds.map((t) => (
          <button
            key={t.value}
            className={`filter-btn ${minCred === t.value ? 'active' : ''}`}
            onClick={() => setMinCred(t.value)}
          >
            {t.label}
          </button>
        ))}
      </div>
      <div className="source-grid">
        {visible.map((s, idx) => (
          <div className="source-card" key={`${s.url}-${idx}`}>
            <div className="source-header">
              <img
                src={`https://www.google.com/s2/favicons?domain=${getDomain(s.url)}&sz=64`}
                alt=""
              />
              <div>
                <a href={s.url} target="_blank" rel="noreferrer">
                  {s.title}
                </a>
                <div className="source-sub">{getDomain(s.url)}</div>
              </div>
            </div>
            <div className="source-meta">
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
      {filtered.length > 6 && (
        <button className="ghost" onClick={() => setShowAll(!showAll)}>
          {showAll ? 'Show less' : 'Show more'}
        </button>
      )}
    </div>
  )
}
