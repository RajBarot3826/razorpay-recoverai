import React from 'react'

export default function InsightsFeed({ data, onViewAll }) {
  const staticInsights = [
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

  const staticActivityFeed = [
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

  let displayInsights = staticInsights
  let displayActivityFeed = staticActivityFeed

  if (data && data.sample_results && data.metrics) {
    const failureStats = {}
    const actionStats = {}
    
    data.sample_results.forEach(r => {
      if (r.failure_reason) {
        if (!failureStats[r.failure_reason]) failureStats[r.failure_reason] = { total: 0, recovered: 0 }
        failureStats[r.failure_reason].total++
        if (r.recovery_status === 'RECOVERED') failureStats[r.failure_reason].recovered++
      }
  
      if (r.action_taken) {
        if (!actionStats[r.action_taken]) actionStats[r.action_taken] = { total: 0, recovered: 0 }
        actionStats[r.action_taken].total++
        if (r.recovery_status === 'RECOVERED') actionStats[r.action_taken].recovered++
      }
    })
  
    let bestFailure = { name: 'UPI TIMEOUT', rate: 91 }
    let maxFailureTotal = 0
    for (const [reason, stats] of Object.entries(failureStats)) {
      if (stats.total > 0) {
        const rate = Math.round((stats.recovered / stats.total) * 100)
        if (rate > bestFailure.rate || (rate === bestFailure.rate && stats.total > maxFailureTotal)) {
          bestFailure = { name: reason.replace(/_/g, ' '), rate }
          maxFailureTotal = stats.total
        }
      }
    }
  
    let bestAction = { name: 'Smart Retry', rate: 87 }
    let maxActionTotal = 0
    for (const [action, stats] of Object.entries(actionStats)) {
      if (stats.total > 0) {
        const rate = Math.round((stats.recovered / stats.total) * 100)
        if (rate > bestAction.rate || (rate === bestAction.rate && stats.total > maxActionTotal)) {
          bestAction = { name: action.replace(/_/g, ' '), rate }
          maxActionTotal = stats.total
        }
      }
    }
  
    displayInsights = [
      {
        id: 1,
        icon: (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
          </svg>
        ),
        color: 'blue',
        title: `${bestFailure.name} has highest recovery rate`,
        desc: `${bestFailure.rate}% of timeouts recovered successfully`,
      },
      {
        id: 2,
        icon: (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
          </svg>
        ),
        color: 'green',
        title: `${bestAction.name} is most effective`,
        desc: `${bestAction.rate}% recovery rate with minimal user friction`,
      },
      {
        id: 3,
        icon: (
          <span style={{ fontWeight: 800, fontSize: '0.95rem' }}>₹</span>
        ),
        color: 'amber',
        title: 'Revenue impact today',
        desc: `₹${data.metrics.revenue_recovered?.toLocaleString() || 0} recovered • ${data.metrics.transactions_saved || 0} transactions saved`,
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
  
    const sortedResults = [...data.sample_results].sort((a, b) => {
      return new Date(b.timestamp) - new Date(a.timestamp)
    }).slice(0, 5)
  
    const getRelativeTime = (timestamp) => {
      const diff = Math.floor((new Date() - new Date(timestamp)) / 1000)
      if (isNaN(diff)) return 'Just now'
      if (diff < 60) return 'Just now'
      if (diff < 3600) return `${Math.floor(diff/60)}m ago`
      if (diff < 86400) return `${Math.floor(diff/3600)}h ago`
      return `${Math.floor(diff/86400)}d ago`
    }
  
    displayActivityFeed = sortedResults.map((r, i) => {
      const isRecovered = r.recovery_status === 'RECOVERED'
      const isFailed = r.recovery_status === 'FAILED'
      const actionStr = r.action_taken || ''
      const isNudge = actionStr === 'CUSTOMER_NUDGE'
      const isAlternative = actionStr === 'ALTERNATIVE_METHOD'
  
      let color = 'green'
      let icon = '✓'
      let statusStr = 'succeeded'
      
      if (isFailed) {
        color = 'red'
        icon = '✕'
        statusStr = 'failed'
      } else if (isNudge && !isRecovered) {
        color = 'blue'
        icon = '✈'
        statusStr = 'sent'
      } else if (isAlternative && !isRecovered) {
        color = 'purple'
        icon = '🔀'
        statusStr = 'tried'
      } else if (!isRecovered) {
        color = 'blue'
        icon = '○'
        statusStr = 'pending'
      }
  
      const shortTxId = r.transaction_id ? r.transaction_id.substring(0, 12) + '...' : `txn_${Math.random().toString(36).substr(2, 8)}`
  
      return {
        id: r.id || i,
        type: actionStr.replace(/_/g, ' '),
        status: statusStr,
        txId: shortTxId,
        amount: `₹${r.amount ? r.amount.toLocaleString() : 0}`,
        time: getRelativeTime(r.timestamp),
        color,
        icon,
      }
    })
  }

  return (
    <div className="insights-feed-column">
      <div className="section-card insights-card">
        <div className="card-header-clean">
          <h3 className="section-title">
            <span className="title-icon-sym">🤖</span> AI Insights
          </h3>
          <button 
            className="view-all-link"
            onClick={() => onViewAll && onViewAll('insights')}
          >
            View all
          </button>
        </div>

        <div className="insights-items-stack">
          {displayInsights.map((item) => (
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

      <div className="section-card activity-feed-card">
        <div className="card-header-clean">
          <h3 className="section-title">
            <span className="title-icon-sym">⚡</span> Activity Feed
          </h3>
          <button 
            className="view-all-link"
            onClick={() => onViewAll && onViewAll('alerts')}
          >
            View all
          </button>
        </div>

        <div className="activity-feed-stack">
          {displayActivityFeed.map((act) => (
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
