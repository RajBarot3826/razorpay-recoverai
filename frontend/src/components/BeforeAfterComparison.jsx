export default function BeforeAfterComparison({ comparison }) {
  if (!comparison) return null

  const { baseline, ai, lift } = comparison
  const baseRate = (baseline.recovery_rate * 100).toFixed(1)
  const aiRate = (ai.recovery_rate * 100).toFixed(1)
  const liftRate = (lift.absolute_rate_increase * 100).toFixed(1)

  return (
    <div className="comparison-section">
      <h3>AI Recovery vs Industry Baseline</h3>
      <div className="comparison-grid">
        <div className="comparison-box baseline">
          <div className="comp-label">Without AI (Baseline)</div>
          <div className="comp-rate">{baseRate}%</div>
          <div className="comp-detail">{baseline.recovered_count} transactions</div>
          <div className="comp-detail">
            ₹{baseline.revenue_recovered.toLocaleString('en-IN', { maximumFractionDigits: 0 })} recovered
          </div>
        </div>

        <div className="comparison-arrow">
          <div className="lift-value">+{liftRate}%</div>
          <div className="lift-label">recovery lift</div>
          <div style={{ marginTop: 8, color: 'var(--success)', fontSize: '0.9rem', fontWeight: 600 }}>
            +{lift.additional_recovered_count} txns
          </div>
          <div style={{ color: 'var(--success)', fontSize: '0.85rem' }}>
            +₹{lift.additional_revenue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          </div>
        </div>

        <div className="comparison-box ai">
          <div className="comp-label">With RecoverAI</div>
          <div className="comp-rate">{aiRate}%</div>
          <div className="comp-detail">{ai.recovered_count} transactions</div>
          <div className="comp-detail">
            ₹{ai.revenue_recovered.toLocaleString('en-IN', { maximumFractionDigits: 0 })} recovered
          </div>
        </div>
      </div>
    </div>
  )
}
