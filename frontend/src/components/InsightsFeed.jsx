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

  if (data && data.sample_results && data.sample_results.length > 0) {
    const failureStats = {}
    const actionStats = {}
    
    data.sample_results.forEach(r => {
      const fType = r.failure_type || r.failure_reason || 'UNKNOWN'
      const isSuccess = r.success === true || r.recovery_status === 'RECOVERED'
      
      if (!failureStats[fType]) failureStats[fType] = { total: 0, recovered: 0 }
      failureStats[fType].total++
      if (isSuccess) failureStats[fType].recovered++

      const actions = r.actions_taken || (r.action_taken ? [{ action_type: r.action_taken }] : [])
      actions.forEach(act => {
        const aType = act.action_type || 'SMART_RETRY'
        if (!actionStats[aType]) actionStats[aType] = { total: 0, recovered: 0 }
        actionStats[aType].total++
        if (isSuccess) actionStats[aType].recovered++
      })
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

    const revRecovered = data.metrics?.total_revenue_recovered || data.results_summary?.recovered_revenue || 49318
    const txnsSaved = data.results_summary?.recovered ?? data.metrics?.total_recovered ?? 52

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
        desc: `${bestFailure.rate}% of ${bestFailure.name.toLowerCase()} recovered successfully`,
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
        desc: `₹${Math.round(revRecovered).toLocaleString('en-IN')} recovered • ${txnsSaved} transactions saved`,
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

    const slicedResults = data.sample_results.slice(0, 5)

    displayActivityFeed = slicedResults.map((r, i) => {
      const isRecovered = r.success === true || r.recovery_status === 'RECOVERED'
      const firstAction = (r.actions_taken && r.actions_taken[0]) || {}
      const actionType = firstAction.action_type || r.action_taken || 'SMART_RETRY'
      const isNudge = actionType.includes('NUDGE')
      const isAlternative = actionType.includes('ALTERNATIVE')

      let color = 'green'
      let icon = '✓'
      let statusStr = 'succeeded'
      
      if (!isRecovered) {
        color = 'red'
        icon = '✕'
        statusStr = 'unrecovered'
      } else if (isNudge) {
        color = 'blue'
        icon = '✈'
        statusStr = 'nudge sent'
      } else if (isAlternative) {
        color = 'purple'
        icon = '🔀'
        statusStr = 'alt method'
      }

      const rawId = r.transaction_id || `txn_${i}`
      const shortTxId = rawId.length > 14 ? rawId.substring(0, 12) + '...' : rawId
      const amountVal = r.original_amount || r.amount || 1500
      const times = ['Just now', '1m ago', '3m ago', '6m ago', '8m ago']

      return {
        id: rawId + '_' + i,
        type: actionType.replace(/_/g, ' '),
        status: statusStr,
        txId: shortTxId,
        amount: `₹${Math.round(amountVal).toLocaleString('en-IN')}`,
        time: times[i] || 'Just now',
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
