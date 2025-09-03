import React, { useState } from 'react'
import './App.css'
import { DifferenceReportWithInputs } from './models'
import DiffViewer from './components/DiffViewer'

const App: React.FC = () => {
  const [data, setData] = useState<DifferenceReportWithInputs | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileUpload: React.ChangeEventHandler<HTMLInputElement> = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      try {
        const parsed = JSON.parse(String(reader.result)) as DifferenceReportWithInputs
        // Basic shape check
        if (!parsed.document_a || !parsed.document_b || !parsed.difference_report?.changes) {
          throw new Error('Invalid JSON shape')
        }
        setData(parsed)
        setError(null)
      } catch (err) {
        setError('Failed to parse JSON. Please provide a valid file.')
      }
    }
    reader.onerror = () => setError('Failed to read file')
    reader.readAsText(file)
  }

  const handleClear = () => setData(null)

  return (
    <div className="app">
      <main className="app-main">
        <div className="topbar">
          <div className="controls inline">
            <label className="upload-btn">
              <input type="file" accept="application/json" onChange={handleFileUpload} />
              Upload JSON
            </label>
            {data && (
              <button className="clear-btn" onClick={handleClear}>Clear</button>
            )}
          </div>
          {error && <p className="error">{error}</p>}
        </div>
        {!data && (
          <div className="placeholder">
            <p>Upload a JSON file that matches the expected schema to view the diff.</p>
          </div>
        )}
        {data && <DiffViewer data={data} />}
      </main>
    </div>
  )
}

export default App
