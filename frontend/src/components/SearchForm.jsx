import React, { useState } from 'react'

export default function SearchForm({ onSearch }) {
  const [field, setField] = useState('srcaddr')
  const [value, setValue] = useState('')
  const [start, setStart] = useState('')
  const [end, setEnd] = useState('')

  const submit = (e) => {
    e.preventDefault()
    const criteria = value ? { [field]: value } : {}
    const starttime = start ? Number(start) : undefined
    const endtime = end ? Number(end) : undefined
    onSearch(criteria, starttime, endtime)
  }

  return (
    <form onSubmit={submit} style={{ marginBottom: 24, display: 'grid', gap: 12, gridTemplateColumns: '1fr 2fr 1fr 1fr auto' }}>
      <select value={field} onChange={(e) => setField(e.target.value)}>
        <option value="srcaddr">srcaddr</option>
        <option value="dstaddr">dstaddr</option>
        <option value="action">action</option>
        <option value="account-id">account-id</option>
        <option value="instance-id">instance-id</option>
      </select>
      <input placeholder="value (e.g. 159.62.125.136)" value={value} onChange={(e) => setValue(e.target.value)} />
      <input placeholder="starttime (epoch)" value={start} onChange={(e) => setStart(e.target.value)} />
      <input placeholder="endtime (epoch)" value={end} onChange={(e) => setEnd(e.target.value)} />
      <button type="submit">Search</button>
    </form>
  )
}




