export default function FailureTypeChart({ data }) {
  // Pre-configured benchmark default data matching reference design
  const defaultItems = [
    { name: 'NETWORK ERROR', recovered: 100, failed: 0, count: 7 },
    { name: 'APP NOT RESPONDING', recovered: 100, failed: 0, count: 7 },
    { name: 'UPI TIMEOUT', recovered: 91, failed: 9, count: 11 },
    { name: 'BANK TIMEOUT', recovered: 64, failed: 36, count: 11 },
    { name: 'INSUFFICIENT FUNDS', recovered: 52, failed: 48, count: 23 },
    { name: 'INCORRECT PIN', recovered: 50, failed: 50, count: 4 },
    { name: 'LIMIT EXCEEDED', recovered: 25, failed: 75, count: 12 },
    { name: 'EXPIRED CARD', recovered: 25, failed: 75, count: 4 },
    { name: 'AUTHENTICATION FAILED', recovered: 17, failed: 83, count: 12 },
    { name: 'RISK BLOCKED', recovered: 0, failed: 100, count: 5 },
  ]

  // If live data is provided, compute rates
  let items = defaultItems
  if (data && Object.keys(data).length > 0) {
    items = Object.entries(data).map(([key, stats]) => {
      const processed = stats.processed || 1
      const recoveredCount = stats.recovered || 0
      const recPct = Math.round((recoveredCount / processed) * 100)
      const failPct = 100 - recPct
      return {
        name: key.replace(/_/g, ' '),
        recovered: recPct,
        failed: failPct,
        count: processed,
      }
    }).sort((a, b) => b.recovered - a.recovered)
  }

  return (
    <div className="section-card failure-type-card">
      <div className="card-header-clean">
        <h3 className="section-title">Recovery by Failure Type</h3>
        <div className="chart-legend-row">
          <span className="legend-item">
            <span className="legend-dot green"></span> Recovered
          </span>
          <span className="legend-item">
            <span className="legend-dot red"></span> Failed
          </span>
        </div>
      </div>

      <div className="custom-horizontal-barchart">
        {items.map((item, idx) => (
          <div key={idx} className="bar-row-item">
            <div className="bar-label-name" title={item.name}>{item.name}</div>
            <div className="bar-track-wrap">
              <div className="stacked-bar-container">
                {item.recovered > 0 && (
                  <div
                    className="bar-segment bar-recovered"
                    style={{ width: `${item.recovered}%` }}
                    title={`Recovered: ${item.recovered}%`}
                  >
                    {item.recovered >= 15 && (
                      <span className="bar-pct-label text-recovered">{item.recovered}%</span>
                    )}
                  </div>
                )}
                {item.failed > 0 && (
                  <div
                    className="bar-segment bar-failed"
                    style={{ width: `${item.failed}%` }}
                    title={`Failed: ${item.failed}%`}
                  >
                    {item.failed >= 15 && (
                      <span className="bar-pct-label text-failed">{item.failed}%</span>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {/* X-Axis Scale */}
        <div className="bar-xaxis-scale">
          <span className="axis-blank-space"></span>
          <div className="axis-ticks-row">
            <span>0</span>
            <span>10</span>
            <span>20</span>
            <span>30</span>
            <span>40</span>
            <span>50</span>
            <span>60</span>
          </div>
        </div>
        <div className="axis-bottom-label">Count</div>
      </div>
    </div>
  )
}
