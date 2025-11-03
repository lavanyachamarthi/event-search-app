import React from 'react'

export default function Results({ results, elapsed, count }) {
  return (
    <div>
      <h3>Results</h3>
      <div style={{ marginBottom: 8 }}>
        <b>Matches:</b> {count} &nbsp;|&nbsp; <b>Search Time:</b> {elapsed.toFixed(2)} seconds
      </div>
      <div style={{ display: 'grid', gap: 8 }}>
        {results && results.length > 0 ? results.map((r, i) => (
          <div key={i} style={{ padding: 12, border: '1px solid #ddd', borderRadius: 8 }}>
            <div>{r.summary}</div>
            <div style={{ fontSize: 12, color: '#666' }}>File: {r.file}</div>
          </div>
        )) : <div>No results yet</div>}
      </div>
    </div>
  )
}




