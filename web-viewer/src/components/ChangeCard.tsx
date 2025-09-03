import React from 'react'
import { Category, ChangeType, ImpactAnalysis } from '../models'

interface ChangeCardProps {
  changeId?: string | null
  category: Category
  changeType: ChangeType
  confidence?: number | null
  location?: string | null
  impact?: ImpactAnalysis | null
  onClose?: () => void
  style?: React.CSSProperties
}

const ChangeCard: React.FC<ChangeCardProps> = ({ changeId, category, changeType, confidence, location, impact, style }) => {
  const frameClass = category === 'Critical' ? 'frame-critical' : category === 'Minor' ? 'frame-minor' : 'frame-formatting'
  const typeBadge = `badge-type-${changeType}`
  const catBadge = `badge-cat-${category}`
  const sevBadge = impact ? `badge-sev-${impact.severity}` : ''

  return (
    <div className={`hover-card ${frameClass}`} style={style}>
      <div className="badge-row">
        {changeId ? <span className="badge badge-id">{"#" + changeId}</span> : null}
        <span className={`badge ${typeBadge}`}>{changeType}</span>
        <span className={`badge ${catBadge}`}>{category}</span>
        {impact?.severity ? <span className={`badge ${sevBadge}`}>severity: {impact.severity}</span> : null}
      </div>
      <div className="row">
        <div className="k">Location</div>
        <div className="v">{location ?? '-'}</div>
      </div>
      {typeof confidence === 'number' ? (
        <div className="row">
          <div className="k">Confidence</div>
          <div className="v">{(confidence * 100).toFixed(0)}%</div>
        </div>
      ) : null}
      {impact ? (
        <>
          <div className="row">
            <div className="k">Party</div>
            <div className="v">{impact.party_affected.join(', ')}</div>
          </div>
          <div className="row">
            <div className="k">Rationale</div>
            <div className="v">{impact.rationale}</div>
          </div>
        </>
      ) : null}
    </div>
  )
}

export default ChangeCard
