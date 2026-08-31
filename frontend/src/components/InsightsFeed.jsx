export default function InsightsFeed() {
  const insights = [
    {
      id: 1,
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
        </svg>
      ),
      color: 'blue',
      title: 'UPI TIMEOUT has highest recovery rate',
      desc: '91% of timeouts recovered successfully',
    },
    {
      id: 2,
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
          <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
        </svg>
      ),
      color: 'green',
      title: 'Smart Retry is most effective',
      desc: '87% recovery rate with minimal user friction',
    },
    {
      id: 3,
      icon: (
        <span style={{ fontWeight: 800, fontSize: '0.95rem' }}>₹</span>
      ),
      color: 'amber',
      title: 'Revenue impact today',
      desc: '₹49,318 recovered • 52 transactions saved',
    },
    {
      id: 4,
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
          <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
          <polyline points="17 6 23 6 23 12"/>
        </svg>
      ),
      color: 'purple',
      title: 'Model Accuracy',
      desc: '98.6% ↑ 28.5% vs last 7 days',
    },
  ]

  const activityFeed = [
    {
      id: 1,
      type: 'SMART RETRY',
      status: 'succeeded',
      txId: 'txn_5fb74451...',
      amount: '₹2,153',
      time: 'Just now',
      color: 'green',
      icon: '✓',
    },
    {
      id: 2,
      type: 'CUSTOMER NUDGE',
      status: 'sent',
      txId: 'txn_a1b2c3d4...',
      amount: '₹1,287',
      time: '2m ago',
      color: 'blue',
      icon: '✈',
    },
    {
      id: 3,
      type: 'RECOVERY FAILED',
      status: '',
      txId: 'txn_e5f6g7h8...',
      amount: '₹843',
      time: '5m ago',
      color: 'red',
      icon: '✕',
    },
    {
      id: 4,
      type: 'ALTERNATIVE METHOD',
      status: 'tried',
      txId: 'txn_i9j0k1l2...',
      amount: '₹2,001',
      time: '7m ago',
      color: 'purple',
      icon: '🔀',
    },
    {
      id: 5,
      type: 'SMART RETRY',
      status: 'succeeded',
      txId: 'txn_m3n4o5p6...',
      amount: '₹3,499',
      time: '9m ago',
      color: 'green',
      icon: '✓',
    },
  ]

  return (
    <div className="insights-feed-column">
      {/* AI Insights Card */}
      <div className="section-card insights-card">
        <div className="card-header-clean">
          <h3 className="section-title">
            <span className="title-icon-sym">🤖</span> AI Insights
          </h3>
          <button className="view-all-link">View all</button>
        </div>

        <div className="insights-items-stack">
          {insights.map((item) => (
            <div key={item.id} className="insight-card-item">
              <div className={`insight-icon-pill icon-${item.color}`}>
                {item.icon}
              </div>
              <div className="insight-body">
                <div className="insight-headline">{item.title}</div>
                <div className="insight-subtext">{item.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Live Activity Feed Card */}
      <div className="section-card activity-feed-card">
        <div className="card-header-clean">
          <h3 className="section-title">
            <span className="title-icon-sym">⚡</span> Live Activity Feed
          </h3>
          <button className="view-all-link">View all</button>
        </div>

        <div className="activity-feed-stack">
          {activityFeed.map((act) => (
            <div key={act.id} className="activity-item-row">
              <div className={`act-dot dot-${act.color}`}>
                {act.icon}
              </div>
              <div className="act-info">
                <div className="act-title">
                  <span className={`act-type text-${act.color}`}>{act.type}</span> {act.status}
                </div>
                <div className="act-details">
                  {act.txId} <span className="act-sep">•</span> {act.amount}
                </div>
              </div>
              <div className="act-time">{act.time}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
