import { Category, ChangeItem } from '../models'

export const categoryClass = (category: Category) =>
  category === 'Critical' ? 'category-critical' : category === 'Minor' ? 'category-minor' : 'category-formatting'

type Highlight = { key: string; cls: string; change: ChangeItem; part: 'old' | 'new'; text: string }

export function buildLineHighlights(
  docALines: string[],
  docBLines: string[],
  changes: ChangeItem[]
): { aMap: Record<number, Highlight[]>; bMap: Record<number, Highlight[]> } {
  const aMap: Record<number, Highlight[]> = {}
  const bMap: Record<number, Highlight[]> = {}

  const ensure = (map: Record<number, Highlight[]>, lineIndex: number) => {
    if (!map[lineIndex]) map[lineIndex] = []
    return map[lineIndex]
  }

  for (let idx = 0; idx < changes.length; idx++) {
    const ch = changes[idx]
    const cls = `change-tag ${categoryClass(ch.change_classification.category)}`
    const oldSrc = ch.diff_hunk?.old_excerpt ?? ch.old_excerpt ?? ''
    const newSrc = ch.diff_hunk?.new_excerpt ?? ch.new_excerpt ?? ''
    const oldLines = oldSrc.split('\n')
    const newLines = newSrc.split('\n')

    const header = ch.diff_hunk?.hunk_header

    const aWindowStart = header ? Math.max(0, (header.start_line_old - 1) - 1) : 0
    const aWindowEnd = header ? Math.min(docALines.length - 1, (header.end_line_old - 1) + 1) : docALines.length - 1
    const bWindowStart = header ? Math.max(0, (header.start_line_new - 1) - 1) : 0
    const bWindowEnd = header ? Math.min(docBLines.length - 1, (header.end_line_new - 1) + 1) : docBLines.length - 1

    for (let i = 0; i < oldLines.length; i++) {
      const needle = oldLines[i].trim()
      if (needle.length < 2) continue
      let matched = false

      for (let lineIdx = aWindowStart; lineIdx <= aWindowEnd; lineIdx++) {
        if (docALines[lineIdx].includes(needle)) {
          ensure(aMap, lineIdx).push({ key: `${ch.change_id ?? idx}-o-${i}-${lineIdx}`, cls, change: ch, part: 'old', text: oldLines[i] })
          matched = true
          break
        }
      }

      if (!matched && !header) {
        for (let lineIdx = 0; lineIdx < docALines.length; lineIdx++) {
          if (docALines[lineIdx].includes(needle)) {
            ensure(aMap, lineIdx).push({ key: `${ch.change_id ?? idx}-o-${i}-${lineIdx}`, cls, change: ch, part: 'old', text: oldLines[i] })
            break
          }
        }
      }
    }

    for (let i = 0; i < newLines.length; i++) {
      const needle = newLines[i].trim()
      if (needle.length < 2) continue
      let matched = false

      for (let lineIdx = bWindowStart; lineIdx <= bWindowEnd; lineIdx++) {
        if (docBLines[lineIdx].includes(needle)) {
          ensure(bMap, lineIdx).push({ key: `${ch.change_id ?? idx}-n-${i}-${lineIdx}`, cls, change: ch, part: 'new', text: newLines[i] })
          matched = true
          break
        }
      }

      if (!matched && !header) {
        for (let lineIdx = 0; lineIdx < docBLines.length; lineIdx++) {
          if (docBLines[lineIdx].includes(needle)) {
            ensure(bMap, lineIdx).push({ key: `${ch.change_id ?? idx}-n-${i}-${lineIdx}`, cls, change: ch, part: 'new', text: newLines[i] })
            break
          }
        }
      }
    }
  }

  return { aMap, bMap }
}


