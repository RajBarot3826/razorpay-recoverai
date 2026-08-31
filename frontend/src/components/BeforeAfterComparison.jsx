export default function BeforeAfterComparison({ comparison }) {
  const baselineRate = (comparison?.baseline?.recovery_rate ? comparison.baseline.recovery_rate * 100 : 15.0).toFixed(1)
  const aiRate = (comparison?.ai?.recovery_rate ? comparison.ai.recovery_rate * 100 : 52.0).toFixed(1)
  const baselineTxns = comparison?.baseline?.recovered_count ?? 15
  const baselineRevenue = comparison?.baseline?.revenue_recovered ? Math.round(comparison.baseline.revenue_recovered) : 14708
  const aiTxns = comparison?.ai?.recovered_count ?? 52
  const aiRevenue = comparison?.ai?.revenue_recovered ? Math.round(comparison.ai.revenue_recovered) : 49318

  const liftRate = (comparison?.lift?.absolute_rate_increase ? comparison.lift.absolute_rate_increase * 100 : 37.0).toFixed(0)
  const extraTxns = comparison?.lift?.additional_recovered_count ?? 37
  const extraRevenue = comparison?.lift?.additional_revenue ? Math.round(comparison.lift.additional_revenue) : 35092

  return (
    <div className="section-card before-after-card">
      <div className="card-header-clean">
        <h3 className="section-title">AI Recovery vs Industry Baseline</h3>
      </div>

      <div className="comparison-content-layout">
        {/* Baseline Box */}
        <div className="comparison-box box-baseline">
          <div className="comp-badge-label">WITHOUT AI (BASELINE)</div>
          <div className="comp-big-number color-red">{baselineRate}%</div>
          <div className="comp-sub-stat">{baselineTxns} transactions</div>
          <div className="comp-sub-stat">₹{baselineRevenue.toLocaleString('en-IN')} recovered</div>
        </div>

        {/* Lift Indicator in center */}
        <div className="comparison-lift-col">
          <div className="lift-badge-val">+{liftRate}% <span className="lift-arrow-sym">↑</span></div>
          <div className="lift-sub-label">recovery lift</div>
          <div className="lift-pills-row">
            <span className="lift-pill">+{extraTxns} txns</span>
            <span className="lift-dot">•</span>
            <span className="lift-pill">+₹{extraRevenue.toLocaleString('en-IN')}</span>
          </div>
        </div>

        {/* AI Box */}
        <div className="comparison-box box-ai">
          <div className="comp-badge-label">WITH RECOVERAI</div>
          <div className="comp-big-number color-green">{aiRate}%</div>
          <div className="comp-sub-stat">{aiTxns} transactions</div>
          <div className="comp-sub-stat">₹{aiRevenue.toLocaleString('en-IN')} recovered</div>
        </div>
      </div>
    </div>
  )
}
