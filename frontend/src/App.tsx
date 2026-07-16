import { useRef, useState } from 'react'
import './App.css'

type ProcessResponse = {
  transcript: string
  summary: string
}

function App() {
  const inputRef = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [summary, setSummary] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  function isMp4(selectedFile: File) {
    return (
      selectedFile.type === 'video/mp4' ||
      selectedFile.name.toLowerCase().endsWith('.mp4')
    )
  }

  function selectFile(selectedFile: File | undefined) {
    if (!selectedFile) return

    if (!isMp4(selectedFile)) {
      setError('Please upload an MP4 video file.')
      setFile(null)
      return
    }

    setFile(selectedFile)
    setError(null)
    setSummary(null)
  }

  function handleDrop(event: React.DragEvent<HTMLDivElement>) {
    event.preventDefault()
    setIsDragging(false)
    selectFile(event.dataTransfer.files[0])
  }

  async function handleSummarize() {
    if (!file) return

    setLoading(true)
    setError(null)
    setSummary(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/process?use_chunking=true', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const data = await response.json().catch(() => null)
        const detail = data?.detail
        throw new Error(
          typeof detail === 'string'
            ? detail
            : 'Failed to summarize the video.',
        )
      }

      const data: ProcessResponse = await response.json()
      setSummary(data.summary)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>AI Video Transcriber</h1>
        <p>Drop an MP4 file below, then summarize it.</p>
      </header>

      <div
        className={`dropzone ${isDragging ? 'dropzone--active' : ''} ${file ? 'dropzone--filled' : ''}`}
        onDragOver={(event) => {
          event.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(event) => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault()
            inputRef.current?.click()
          }
        }}
        role="button"
        tabIndex={0}
        aria-label="Upload MP4 video"
      >
        <input
          ref={inputRef}
          type="file"
          accept="video/mp4,.mp4"
          hidden
          onChange={(event) => selectFile(event.target.files?.[0])}
        />

        {file ? (
          <>
            <span className="dropzone__label">Selected file</span>
            <strong className="dropzone__filename">{file.name}</strong>
            <span className="dropzone__hint">Drop another file to replace it</span>
          </>
        ) : (
          <>
            <span className="dropzone__label">Drag & drop your MP4 here</span>
            <span className="dropzone__hint">or click to browse</span>
          </>
        )}
      </div>

      <button
        type="button"
        className="summarize-btn"
        onClick={handleSummarize}
        disabled={!file || loading}
      >
        {loading ? 'Summarizing...' : 'Summarize'}
      </button>

      {error && <p className="message message--error">{error}</p>}

      {loading && (
        <p className="message message--loading">
          Processing video. This may take a few minutes.
        </p>
      )}

      {summary && (
        <section className="summary">
          <h2>Summary</h2>
          <p>{summary}</p>
        </section>
      )}
    </div>
  )
}

export default App
