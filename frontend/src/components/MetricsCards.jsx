export default function MetricsCards({ metrics, summary }) {
  const total = summary?.total ?? metrics?.total_processed ?? 100
  const recovered = summary?.recovered ?? metrics?.total_recovered ?? 52
  const failed = summary?.failed ?? metrics?.total_failed ?? 48
  const revenue = metrics?.total_revenue_recovered ?? 49318
  const recoveryRate = (metrics?.recovery_rate != null ? metrics.recovery_rate * 100 : 52).toFixed(1)

  const cards = [
    {
      id: 'processed',
      title: 'TOTAL PROCESSED',
      value: total.toLocaleString(),
      subtitle: 'failed transactions analyzed',
      trend: '18.6% vs yesterday',
      trendUp: true,
      color: 'blue',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
          <path d="M6 12v5c3 3 9 3 12 0v-5"/>
        </svg>
      ),
      sparklinePoints: '0,20 15,18 30,12 45,15 60,8 75,10 90,4 100,6',
    },
    {
      id: 'recovered',
      title: 'RECOVERED',
      value: recovered.toLocaleString(),
      subtitle: `${recoveryRate}% recovery rate`,
      trend: '24.7% vs yesterday',
      trendUp: true,
      color: 'green',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
          <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
      ),
      sparklinePoints: '0,22 15,19 30,15 45,18 60,10 75,8 90,3 100,5',
    },
    {
      id: 'failed',
      title: 'NOT RECOVERED',
      value: failed.toLocaleString(),
      subtitle: 'unrecoverable failures',
      trend: '8.3% vs yesterday',
      trendUp: false,
      color: 'red',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="15" y1="9" x2="9" y2="15"/>
          <line x1="9" y1="9" x2="15" y2="15"/>
        </svg>
      ),
      sparklinePoints: '0,10 15,12 30,18 45,14 60,20 75,16 90,22 100,19',
    },
    {
      id: 'revenue',
      title: 'REVENUE RECOVERED',
      value: `₹ ${Math.round(revenue).toLocaleString('en-IN')}`,
      subtitle: 'saved from failed payments',
      trend: '31.2% vs yesterday',
      trendUp: true,
      color: 'gold',
      icon: (
        <span style={{ fontSize: '18px', fontWeight: 800, fontFamily: 'system-ui' }}>₹</span>
      ),
      sparklinePoints: '0,24 15,22 30,19 45,17 60,12 75,10 90,5 100,4',
    },
    {
      id: 'rate',
      title: 'RECOVERY RATE',
      value: `${recoveryRate}%`,
      subtitle: 'vs 15% industry baseline',
      trend: '37.0% vs yesterday',
      trendUp: true,
      color: 'purple',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <line x1="18" y1="20" x2="18" y2="10"/>
          <line x1="12" y1="20" x2="12" y2="4"/>
          <line x1="6" y1="20" x2="6" y2="14"/>
        </svg>
      ),
      sparklinePoints: '0,20 15,16 30,18 45,12 60,14 75,8 90,6 100,2',
    },
  ]

  return (
    <div className="metrics-cards-row">
      {cards.map((card) => (
        <div key={card.id} className={`metric-card border-${card.color}`}>
          <div className="card-top-header">
            <span className="card-title-text">{card.title}</span>
            <span className="card-dots-icon">•••</span>
          </div>

          <div className="card-primary-content">
            <div className={`metric-icon-box bg-${card.color}`}>
              {card.icon}
            </div>
            <div className="metric-value-number">{card.value}</div>
          </div>

          <div className="metric-subtitle-text">{card.subtitle}</div>

          <div className="card-bottom-sparkline-row">
            <div className={`trend-indicator-text ${card.trendUp ? 'trend-green' : 'trend-red'}`}>
              <span className="trend-arrow">{card.trendUp ? '↑' : '↓'}</span>
              {card.trend}
            </div>
            <div className="sparkline-wrapper">
              <svg width="72" height="24" viewBox="0 0 100 24" fill="none">
                <polyline
                  points={card.sparklinePoints}
                  className={`sparkline-path stroke-${card.color}`}
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
