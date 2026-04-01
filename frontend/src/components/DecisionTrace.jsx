import { useState } from 'react'

export default function DecisionTrace({ trace }) {
  const [open, setOpen] = useState(false)
  if (!trace) return null

  return (
    <div className="card">
      <div className="trace-header">
        <h3>Decision Trace</h3>
        <button className="ghost" onClick={() => setOpen(!open)}>
          {open ? 'Hide' : 'Show'}
        </button>
      </div>
      {open && (
        <pre className="trace-box">{JSON.stringify(trace, null, 2)}</pre>
      )}
    </div>
  )
}