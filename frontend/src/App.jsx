import React, { useState } from 'react'
import UploadSection from './components/UploadSection.jsx'
import SearchForm from './components/SearchForm.jsx'
import Results from './components/Results.jsx'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'

export default function App() {
  const [results, setResults] = useState([])
  const [elapsed, setElapsed] = useState(0)
  const [count, setCount] = useState(0)

  const onSearch = async (criteria, starttime, endtime) => {
    const res = await fetch(`${API_BASE}/search/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ criteria, starttime, endtime })
    })
    const data = await res.json()
    setResults(data.results || [])
    setElapsed(data.elapsed_seconds || 0)
    setCount(data.count || 0)
  }

  const onUpload = async (files) => {
    const form = new FormData()
    for (const f of files) form.append('files', f)
    await fetch(`${API_BASE}/upload/`, { method: 'POST', body: form })
  }

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: 24, fontFamily: 'Inter, system-ui, Arial' }}>
      <h2>Event Search</h2>
      <UploadSection onUpload={onUpload} />
      <SearchForm onSearch={onSearch} />
      <Results results={results} elapsed={elapsed} count={count} />
    </div>
  )
}




