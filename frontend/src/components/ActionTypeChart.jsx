export default function ActionTypeChart({ data }) {
  let smartRetry = 87
  let altMethod = 12
  let escalation = 1
  let totalCount = 100

  if (data && Object.keys(data).length > 0) {
    const sr = data.SMART_RETRY?.processed || 0
    const am = data.ALTERNATIVE_METHOD?.processed || 0
    const esc = data.ESCALATION?.processed || 0
    const sum = sr + am + esc || 100
    totalCount = sum
    smartRetry = Math.round((sr / sum) * 100) || 87
    altMethod = Math.round((am / sum) * 100) || 12
    escalation = Math.max(1, 100 - smartRetry - altMethod)
  }

  const radius = 54
  const circumference = 2 * Math.PI * radius

  const srStroke = (smartRetry / 100) * circumference
  const amStroke = (altMethod / 100) * circumference
  const escStroke = (escalation / 100) * circumference

  const srOffset = 0
  const amOffset = -srStroke
  const escOffset = -(srStroke + amStroke)

  return (
    <div className="section-card action-type-card">
      <div className="card-header-clean">
        <h3 className="section-title">Actions by Type</h3>
      </div>

      <div className="donut-chart-wrapper">
        <div className="donut-svg-container">
          <svg className="donut-svg" viewBox="0 0 140 140">
            <circle
              cx="70"
              cy="70"
              r={radius}
              fill="none"
              stroke="#f1f5f9"
              strokeWidth="16"
            />

            <circle
              cx="70"
              cy="70"
              r={radius}
              fill="none"
              stroke="#3b82f6"
              strokeWidth="16"
              strokeDasharray={`${srStroke} ${circumference}`}
              strokeDashoffset={srOffset}
              transform="rotate(-90 70 70)"
            />

            <circle
              cx="70"
              cy="70"
              r={radius}
              fill="none"
              stroke="#10b981"
              strokeWidth="16"
              strokeDasharray={`${amStroke} ${circumference}`}
              strokeDashoffset={amOffset}
              transform="rotate(-90 70 70)"
            />

            <circle
              cx="70"
              cy="70"
              r={radius}
              fill="none"
              stroke="#f59e0b"
              strokeWidth="16"
              strokeDasharray={`${escStroke} ${circumference}`}
              strokeDashoffset={escOffset}
              transform="rotate(-90 70 70)"
            />
          </svg>

          <div className="donut-center-text">
            <span className="donut-center-total">{totalCount}</span>
            <span className="donut-center-label">actions</span>
          </div>
        </div>

        <div className="donut-legend-column">
          <div className="donut-legend-entry">
            <span className="legend-marker bg-blue"></span>
            <span className="legend-text-label">SMART RETRY</span>
            <span className="legend-pct-val">{smartRetry}%</span>
          </div>

          <div className="donut-legend-entry">
            <span className="legend-marker bg-green"></span>
            <span className="legend-text-label">ALTERNATIVE METHOD</span>
            <span className="legend-pct-val">{altMethod}%</span>
          </div>

          <div className="donut-legend-entry">
            <span className="legend-marker bg-gold"></span>
            <span className="legend-text-label">ESCALATION</span>
            <span className="legend-pct-val">{escalation}%</span>
          </div>
        </div>
      </div>
    </div>
  )
}
