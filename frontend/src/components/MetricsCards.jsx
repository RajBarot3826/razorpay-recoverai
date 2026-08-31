export default function MetricsCards({ metrics, summary }) {
  const recoveryRate = (metrics.recovery_rate * 100).toFixed(1)
  const revenue = metrics.total_revenue_recovered || 0

  return (
    <div className="metrics-grid">
      <div className="metric-card accent">
        <div className="label">Total Processed</div>
        <div className="value">{metrics.total_processed}</div>
        <div className="sub">failed transactions analyzed</div>
      </div>

      <div className="metric-card success">
        <div className="label">Recovered</div>
        <div className="value">{metrics.total_recovered}</div>
        <div className="sub">{recoveryRate}% recovery rate</div>
      </div>

      <div className="metric-card danger">
        <div className="label">Not Recovered</div>
        <div className="value">{metrics.total_failed}</div>
        <div className="sub">unrecoverable failures</div>
      </div>

      <div className="metric-card warning">
        <div className="label">Revenue Recovered</div>
        <div className="value">₹{revenue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
        <div className="sub">saved from failed payments</div>
      </div>

      <div className="metric-card purple">
        <div className="label">Recovery Rate</div>
        <div className="value">{recoveryRate}%</div>
        <div className="sub">vs 15% industry baseline</div>
      </div>
    </div>
  )
}
