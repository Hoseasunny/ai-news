import { useState } from 'react'

const MIN_LEN = 10

export default function InputForm({ onSubmit, isLoading }) {
  const [text, setText] = useState('')
  const [error, setError] = useState(null)

  const handleSubmit = (e) => {
    e.preventDefault()
    const trimmed = text.trim()
    if (trimmed.length < MIN_LEN) {
      setError(`Input too short (min ${MIN_LEN} characters)`) 
      return
    }
    setError(null)
    onSubmit(trimmed)
  }

  return (
    <form className="card input-card" onSubmit={handleSubmit}>
      <label className="label" htmlFor="news-input">News Text or Headline</label>
      <textarea
        id="news-input"
        rows={5}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste a headline or a short news paragraph..."
      />
      <div className="input-row">
        <span className={`char-count ${text.trim().length < MIN_LEN ? 'warn' : ''}`}>
          {text.trim().length}/{MIN_LEN}+
        </span>
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Verifying...' : 'Verify'}
        </button>
      </div>
      {error && <p className="error">{error}</p>}
    </form>
  )
}