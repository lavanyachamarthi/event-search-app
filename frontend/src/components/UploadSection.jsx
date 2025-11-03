import React, { useState } from 'react'

export default function UploadSection({ onUpload }) {
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState('')

  const handleChange = async (e) => {
    const files = e.target.files
    if (!files || files.length === 0) return
    setBusy(true)
    setMsg('Uploading...')
    try {
      await onUpload(files)
      setMsg('Uploaded successfully')
    } catch (e) {
      setMsg('Upload failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ marginBottom: 24 }}>
      <h3>Upload Event Files</h3>
      <input type="file" multiple onChange={handleChange} disabled={busy} />
      <div style={{ fontSize: 12, color: '#555', marginTop: 6 }}>{msg}</div>
    </div>
  )
}




