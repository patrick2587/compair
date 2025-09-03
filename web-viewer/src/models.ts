export type ChangeType = 'added' | 'removed' | 'modified' | 'moved'
export type Category = 'Critical' | 'Minor' | 'Formatting'

export interface ImpactAnalysis {
  severity: 'low' | 'medium' | 'high'
  party_affected: Array<'Data Controller' | 'Data Processor' | 'Both'>
  rationale: string
}

export interface ChangeClassification {
  change_type: ChangeType
  category: Category
  confidence?: number | null
  location?: string | null
  impact_analysis?: ImpactAnalysis | null
}

export interface HunkHeader {
  start_line_old: number
  end_line_old: number
  start_line_new: number
  end_line_new: number
}

export interface DiffHunk {
  unified_diff: string
  old_excerpt: string | null
  new_excerpt: string | null
  hunk_header: HunkHeader
}

export interface ChangeItem {
  change_id?: string | null
  old_excerpt?: string | null
  new_excerpt?: string | null
  change_classification: ChangeClassification
  diff_hunk?: DiffHunk | null
}

export interface DifferenceReport {
  changes: ChangeItem[]
  summary?: string | null
}

export interface DifferenceReportWithInputs {
  document_a: string
  document_b: string
  difference_report: DifferenceReport
}

// Runtime-normalized change that supports multiple input schemas
export interface NormalizedChange {
  change_id: string
  old_excerpt: string | null
  new_excerpt: string | null
  category: Category
  change_type: ChangeType
  confidence: number | null
  location: string | null
  impact_analysis: ImpactAnalysis | null
  diff_hunk?: DiffHunk | null
}


