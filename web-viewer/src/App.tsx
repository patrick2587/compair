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

  const handleExportCsv = () => {
    if (!data) return
    const critical = (data.difference_report?.changes ?? []).filter(
      (c) => c.change_classification?.category === 'Critical'
    )

    const q = (v: string | null | undefined) => {
      const s = String(v ?? '').replace(/\r?\n/g, ' ').trim()
      return `"${s.replace(/"/g, '""')}"`
    }

    const header = [
      'change_id',
      'location',
      'change_type',
      'severity',
      'party_affected',
      'rationale',
      'summary',
      'old_excerpt',
      'new_excerpt'
    ].map(q).join(',')

    const rows = critical.map(ch => {
      const cls = ch.change_classification
      const ia = cls?.impact_analysis ?? null
      const severity = ia?.severity ?? ''
      const party = ia?.party_affected?.join(' | ') ?? ''
      const rationale = ia?.rationale ?? ''
      const oldEx = ch.diff_hunk?.old_excerpt ?? ch.old_excerpt ?? ''
      const newEx = ch.diff_hunk?.new_excerpt ?? ch.new_excerpt ?? ''
      return [
        q(ch.change_id ?? ''),
        q(cls?.location ?? ''),
        q(cls?.change_type ?? ''),
        q(severity),
        q(party),
        q(rationale),
        q(cls?.summary ?? ''),
        q(oldEx),
        q(newEx)
      ].join(',')
    })

    const csv = [header, ...rows].join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'critical-changes.csv'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

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
              <>
                <button className="clear-btn" onClick={handleExportCsv}>Export CSV (Critical)</button>
                <button className="clear-btn" onClick={handleClear}>Clear</button>
              </>
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