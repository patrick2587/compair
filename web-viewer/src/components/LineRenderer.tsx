import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkBreaks from 'remark-breaks'
import rehypeRaw from 'rehype-raw'
import { ChangeItem } from '../models'

type Highlight = { key: string; cls: string; change: ChangeItem; part: 'old' | 'new'; text: string }

interface LineRendererProps {
  line: string
  lineIdx: number
  side: 'a' | 'b'
  aMap: Record<number, Highlight[]>
  bMap: Record<number, Highlight[]>
  onShowHover: (x: number, y: number, change: ChangeItem) => void
  onHideHover: () => void
}

const LineRenderer: React.FC<LineRendererProps> = ({ line, lineIdx, side, aMap, bMap, onShowHover, onHideHover }) => {
  const list = side === 'a' ? aMap[lineIdx] : bMap[lineIdx]

  if (!list || list.length === 0) {
    return (
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]} rehypePlugins={[rehypeRaw]}>
        {line || '\u00A0'}
      </ReactMarkdown>
    )
  }

  return (
    <>
      {list.map(h => (
        <div
          key={h.key}
          className={h.cls}
          onMouseEnter={(e) => {
            const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
            onShowHover(rect.left + window.scrollX + 8, rect.top + window.scrollY + rect.height + 8, h.change)
          }}
          onMouseLeave={onHideHover}
          style={{ cursor: 'help' }}
        >
          <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]} rehypePlugins={[rehypeRaw]}>
            {line || '\u00A0'}
          </ReactMarkdown>
        </div>
      ))}
    </>
  )
}

export default LineRenderer


