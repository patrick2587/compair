import React, { useEffect, useMemo, useRef, useState } from 'react'
import { ChangeItem, DifferenceReportWithInputs } from '../models'
import { buildLineHighlights } from '../utils/diffUtils'
import ChangeCard from './ChangeCard'
import LineRenderer from './LineRenderer'

interface DiffViewerProps {
  data: DifferenceReportWithInputs
}

const DiffViewer: React.FC<DiffViewerProps> = ({ data }) => {
  const { document_a, document_b, difference_report } = data
  const changes = difference_report.changes

  const linesA = useMemo(() => document_a.split('\n'), [document_a])
  const linesB = useMemo(() => document_b.split('\n'), [document_b])

  const { aMap, bMap } = useMemo(() => buildLineHighlights(linesA, linesB, changes), [linesA, linesB, changes])

  // hover card state
  const [hoverInfo, setHoverInfo] = useState<{
    x: number
    y: number
    change: ChangeItem
  } | null>(null)

  // synced scrolling
  const leftRef = useRef<HTMLDivElement | null>(null)
  const rightRef = useRef<HTMLDivElement | null>(null)
  const syncing = useRef(false)

  useEffect(() => {
    const left = leftRef.current
    const right = rightRef.current
    if (!left || !right) return

    const onLeft = () => {
      if (syncing.current) return
      syncing.current = true
      const ratio = left.scrollTop / (left.scrollHeight - left.clientHeight || 1)
      right.scrollTop = ratio * (right.scrollHeight - right.clientHeight)
      syncing.current = false
    }
    const onRight = () => {
      if (syncing.current) return
      syncing.current = true
      const ratio = right.scrollTop / (right.scrollHeight - right.clientHeight || 1)
      left.scrollTop = ratio * (left.scrollHeight - left.clientHeight)
      syncing.current = false
    }

    left.addEventListener('scroll', onLeft)
    right.addEventListener('scroll', onRight)
    return () => {
      left.removeEventListener('scroll', onLeft)
      right.removeEventListener('scroll', onRight)
    }
  }, [])

  return (
    <div className="diff-layout">
      <div className="diff-container">
        <div className="pane">
          <h2>Document A</h2>
          <div className="markdown" ref={leftRef}>
            {linesA.map((line, i) => (
              <div key={i}>
                <LineRenderer
                  line={line}
                  lineIdx={i}
                  side='a'
                  aMap={aMap}
                  bMap={bMap}
                  onShowHover={(x, y, change) => setHoverInfo({ x, y, change })}
                  onHideHover={() => setHoverInfo(null)}
                />
              </div>
            ))}
          </div>
        </div>
        <div className="pane">
          <h2>Document B</h2>
          <div className="markdown" ref={rightRef}>
            {linesB.map((line, i) => (
              <div key={i}>
                <LineRenderer
                  line={line}
                  lineIdx={i}
                  side='b'
                  aMap={aMap}
                  bMap={bMap}
                  onShowHover={(x, y, change) => setHoverInfo({ x, y, change })}
                  onHideHover={() => setHoverInfo(null)}
                />
              </div>
            ))}
          </div>
        </div>
      </div>

      {hoverInfo ? (
        <ChangeCard
          changeId={hoverInfo.change.change_id ?? undefined}
          category={hoverInfo.change.change_classification.category}
          changeType={hoverInfo.change.change_classification.change_type}
          confidence={hoverInfo.change.change_classification.confidence ?? undefined}
          location={hoverInfo.change.change_classification.location ?? undefined}
          impact={hoverInfo.change.change_classification.impact_analysis ?? null}
          style={{ left: hoverInfo.x, top: hoverInfo.y }}
        />
      ) : null}
    </div>
  )
}

export default DiffViewer
