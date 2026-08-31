import { useState, Fragment } from 'react'

export default function TransactionTable({ results }) {
  const [expandedId, setExpandedId] = useState('txn_f229804a...')
  const [currentPage, setCurrentPage] = useState(1)

  const defaultTransactions = [
    {
      transaction_id: 'txn_5fb74451a09b40c6',
      display_id: 'txn_5fb74451...',
      original_amount: 2153,
      failure_type: 'UPI TIMEOUT',
      root_cause: 'Network timeout during transaction',
      success: true,
      actions_count: '1 action(s)',
      time: '31 May, 11:32 AM',
      confidence_score: 0.88,
      actions_taken: [
        { action_type: 'SMART RETRY', status: 'SCHEDULED', outcome: 'Recovery successful (prob=75%)' },
      ],
      audit_trail: [
        { agent_name: 'FailureClassifier', action: 'CLASSIFY', outcome: 'success' },
        { agent_name: 'RootCauseAnalyzer', action: 'ANALYZE', outcome: 'severity=LOW' },
        { agent_name: 'StrategyEngine', action: 'DECIDE_STRATEGY', outcome: 'SMART_RETRY' },
        { agent_name: 'SMART_RETRYAgent', action: 'EXECUTE', outcome: 'Recovery successful (prob=75%)' },
      ],
    },
    {
      transaction_id: 'txn_2cc0f245b2a9',
      display_id: 'txn_2cc0f245...',
      original_amount: 1449,
      failure_type: 'INSUFFICIENT FUNDS',
      has_diamond: true,
      root_cause: 'Bank declined due to NSF',
      success: false,
      actions_count: '2 action(s)',
      time: '31 May, 11:28 AM',
      confidence_score: 0.42,
      actions_taken: [
        { action_type: 'SMART RETRY', status: 'SCHEDULED', outcome: 'Retry attempted but failed (NSF)' },
        { action_type: 'CUSTOMER NUDGE', status: 'COMPLETED', outcome: 'Nudge sent via WhatsApp' },
      ],
      audit_trail: [
        { agent_name: 'FailureClassifier', action: 'CLASSIFY', outcome: 'success' },
        { agent_name: 'RootCauseAnalyzer', action: 'ANALYZE', outcome: 'severity=MEDIUM' },
        { agent_name: 'StrategyEngine', action: 'DECIDE_STRATEGY', outcome: 'SMART_RETRY' },
      ],
    },
    {
      transaction_id: 'txn_7a8d3b90...',
      display_id: 'txn_7a8d3b90...',
      original_amount: 3842,
      failure_type: 'BANK TIMEOUT',
      root_cause: 'Bank system timeout',
      success: false,
      actions_count: '1 action(s)',
      time: '31 May, 11:22 AM',
      confidence_score: 0.65,
      actions_taken: [
        { action_type: 'SMART RETRY', status: 'SCHEDULED', outcome: 'Scheduled for retry in 5 mins' },
      ],
      audit_trail: [
        { agent_name: 'FailureClassifier', action: 'CLASSIFY', outcome: 'success' },
        { agent_name: 'RootCauseAnalyzer', action: 'ANALYZE', outcome: 'severity=LOW' },
      ],
    },
    {
      transaction_id: 'txn_f229804a...',
      display_id: 'txn_f229804a...',
      original_amount: 980,
      failure_type: 'INCORRECT PIN',
      root_cause: 'Customer entered wrong PIN',
      success: true,
      actions_count: '2 action(s)',
      time: '31 May, 11:15 AM',
      confidence_score: 0.94,
      actions_taken: [
        { action_type: 'CUSTOMER NUDGE', status: 'BLOCKED', outcome: 'Blocked by quiet hours guardrail (22:00)' },
        { action_type: 'SMART RETRY', status: 'COMPLETED', outcome: 'Retry succeeded after user updated PIN' },
      ],
      audit_trail: [
        { agent_name: 'FailureClassifier', action: 'CLASSIFY', outcome: 'success' },
        { agent_name: 'RootCauseAnalyzer', action: 'ANALYZE', outcome: 'severity=LOW' },
        { agent_name: 'StrategyEngine', action: 'DECIDE_STRATEGY', outcome: 'CUSTOMER_NUDGE' },
        { agent_name: 'ComplianceGuardrail', action: 'CHECK_QUIET_HOURS', outcome: 'BLOCKED (Quiet Hours 21:00-08:00)' },
      ],
    },
    {
      transaction_id: 'txn_b891e43c...',
      display_id: 'txn_b891e43c...',
      original_amount: 4500,
      failure_type: 'LIMIT EXCEEDED',
      root_cause: 'Daily transaction limit exceeded',
      success: false,
      actions_count: '1 action(s)',
      time: '31 May, 10:55 AM',
      confidence_score: 0.72,
      actions_taken: [
        { action_type: 'ALTERNATIVE METHOD', status: 'COMPLETED', outcome: 'Sent alternative payment link' },
      ],
      audit_trail: [
        { agent_name: 'FailureClassifier', action: 'CLASSIFY', outcome: 'success' },
        { agent_name: 'RootCauseAnalyzer', action: 'ANALYZE', outcome: 'severity=HIGH' },
        { agent_name: 'StrategyEngine', action: 'DECIDE_STRATEGY', outcome: 'ALTERNATIVE_METHOD' },
      ],
    },
  ]

  const formatTimestamp = (index) => {
    const d = new Date(Date.now() - (index * 75000 + 120000))
    const day = d.getDate()
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    const month = months[d.getMonth()]
    let hours = d.getHours()
    const minutes = d.getMinutes().toString().padStart(2, '0')
    const ampm = hours >= 12 ? 'PM' : 'AM'
    hours = hours % 12
    hours = hours ? hours : 12
    return `${day} ${month}, ${hours}:${minutes} ${ampm}`
  }

  const rawTransactions = results && results.length > 0
    ? results.map((r, index) => ({
        transaction_id: r.transaction_id,
        display_id: r.transaction_id.length > 12 ? `${r.transaction_id.substring(0, 12)}...` : r.transaction_id,
        original_amount: r.original_amount,
        failure_type: (r.failure_type || 'UNKNOWN').replace(/_/g, ' '),
        has_diamond: (r.failure_type || '').includes('FUNDS'),
        root_cause: r.root_cause || 'Payment processing error',
        success: r.success,
        actions_count: `${r.actions_taken ? r.actions_taken.length : 1} action(s)`,
        time: formatTimestamp(index),
        confidence_score: r.confidence_score || 0.85,
        actions_taken: r.actions_taken && r.actions_taken.length > 0 
          ? r.actions_taken 
          : [{ action_type: 'SMART RETRY', status: 'SCHEDULED', outcome: 'Scheduled for automatic retry' }],
        audit_trail: r.audit_trail && r.audit_trail.length > 0 
          ? r.audit_trail 
          : [
              { agent_name: 'FailureClassifier', action: 'CLASSIFY', outcome: 'success' },
              { agent_name: 'RootCauseAnalyzer', action: 'ANALYZE', outcome: 'severity=LOW' },
              { agent_name: 'StrategyEngine', action: 'DECIDE_STRATEGY', outcome: 'SMART_RETRY' }
            ],
      }))
    : defaultTransactions

  const itemsPerPage = 10
  const totalItems = rawTransactions.length
  const totalPages = Math.max(1, Math.ceil(totalItems / itemsPerPage))
  
  const safeCurrentPage = Math.min(Math.max(1, currentPage), totalPages)
  const startIndex = (safeCurrentPage - 1) * itemsPerPage
  const endIndex = Math.min(startIndex + itemsPerPage, totalItems)
  const currentTransactions = rawTransactions.slice(startIndex, endIndex)
  
  const showingStart = totalItems > 0 ? startIndex + 1 : 0
  const showingEnd = endIndex

  const handlePageClick = (page) => {
    setCurrentPage(page)
  }

  const handlePrevPage = () => {
    if (safeCurrentPage > 1) {
      setCurrentPage(safeCurrentPage - 1)
    }
  }

  const handleNextPage = () => {
    if (safeCurrentPage < totalPages) {
      setCurrentPage(safeCurrentPage + 1)
    }
  }

  const getPageNumbers = () => {
    if (totalPages <= 5) {
      return Array.from({ length: totalPages }, (_, i) => i + 1)
    }
    
    if (safeCurrentPage <= 3) {
      return [1, 2, 3, '...', totalPages]
    }
    
    if (safeCurrentPage >= totalPages - 2) {
      return [1, '...', totalPages - 2, totalPages - 1, totalPages]
    }
    
    return [1, '...', safeCurrentPage, '...', totalPages]
  }

  return (
    <div className="section-card transaction-table-card">
      <div className="card-header-clean">
        <h3 className="section-title">
          Transaction Details <span className="title-count-paren">({totalItems} total)</span>
        </h3>
      </div>

      <div className="table-responsive-wrapper">
        <table className="custom-tx-table">
          <thead>
            <tr>
              <th className="col-txid">TRANSACTION ID</th>
              <th className="col-amount">AMOUNT</th>
              <th className="col-failure">FAILURE TYPE</th>
              <th className="col-rootcause">ROOT CAUSE</th>
              <th className="col-status">STATUS</th>
              <th className="col-actions">ACTIONS</th>
              <th className="col-time">TIME</th>
            </tr>
          </thead>
          <tbody>
            {currentTransactions.map((tx) => {
              const isExpanded = expandedId === tx.transaction_id || expandedId === tx.display_id
              return (
                <Fragment key={tx.transaction_id}>
                  <tr
                    className={`tx-row-item ${isExpanded ? 'row-expanded' : ''}`}
                    onClick={() => setExpandedId(isExpanded ? null : tx.transaction_id)}
                  >
                    <td className="col-txid">
                      <span className="tx-id-link">{tx.display_id}</span>
                    </td>
                    <td className="col-amount">
                      <span className="tx-amount-val">₹{tx.original_amount.toLocaleString('en-IN')}</span>
                    </td>
                    <td className="col-failure">
                      <span className="tx-failure-pill">
                        {tx.has_diamond && <span className="diamond-bullet">◆</span>}
                        {tx.failure_type}
                      </span>
                    </td>
                    <td className="col-rootcause">
                      <span className="tx-root-cause-text">{tx.root_cause}</span>
                    </td>
                    <td className="col-status">
                      <span className={`status-badge-pill ${tx.success ? 'success' : 'failed'}`}>
                        <span className="status-sym">{tx.success ? '✓' : '✕'}</span>
                        {tx.success ? 'Recovered' : 'Failed'}
                      </span>
                    </td>
                    <td className="col-actions">
                      <span className="tx-actions-count">{tx.actions_count}</span>
                    </td>
                    <td className="col-time">
                      <div className="tx-time-wrapper">
                        <span className="tx-time-text">{tx.time}</span>
                        <span className={`expand-chevron ${isExpanded ? 'open' : ''}`}>›</span>
                      </div>
                    </td>
                  </tr>

                  {isExpanded && (
                    <tr className="tx-audit-detail-row">
                      <td colSpan="7">
                        <div className="audit-panel-grid">
                          <div className="audit-left-info">
                            <div className="audit-section-heading">ML CONFIDENCE SCORE</div>
                            <div className="audit-confidence-block">
                              <span className="confidence-score-number">
                                {Math.round(tx.confidence_score * 100)}%
                              </span>
                              <span className="confidence-meter-bar">
                                <span
                                  className="confidence-fill"
                                  style={{ width: `${Math.round(tx.confidence_score * 100)}%` }}
                                ></span>
                              </span>
                            </div>
                            <div className="audit-meta-line">
                              <span className="meta-key">Failure Category:</span>
                              <span className="meta-val">{tx.failure_type}</span>
                            </div>
                            <div className="audit-meta-line">
                              <span className="meta-key">Root Diagnostic:</span>
                              <span className="meta-val">{tx.root_cause}</span>
                            </div>
                          </div>

                          <div className="audit-middle-actions">
                            <div className="audit-section-heading">RECOVERY ACTIONS</div>
                            <div className="action-items-list">
                              {tx.actions_taken.map((act, i) => (
                                <div
                                  key={i}
                                  className={`action-trail-row border-${act.status === 'BLOCKED' ? 'red' : 'green'}`}
                                >
                                  <span className="action-name-text">{(act.action_type || '').replace(/_/g, ' ')}</span>
                                  <span className={`action-status-badge badge-${(act.status || '').toLowerCase()}`}>
                                    {act.status}
                                  </span>
                                  <span className="action-outcome-text">
                                    {act.outcome || (typeof act.details === 'string' ? act.details : 'Completed')}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>

                          <div className="audit-right-trail">
                            <div className="audit-section-heading">FULL AUDIT TRAIL</div>
                            <div className="audit-timeline-flow">
                              {tx.audit_trail.map((entry, idx) => {
                                const isExec = entry.agent_name.includes('Agent') || idx === tx.audit_trail.length - 1
                                return (
                                  <div key={idx} className="timeline-node-item">
                                    <span className={`timeline-node-dot ${isExec ? 'green' : 'blue'}`}></span>
                                    <span className="node-agent-name">{entry.agent_name}</span>
                                    <span className="node-action-verb">{entry.action}</span>
                                    <span className="node-result-desc">{entry.outcome}</span>
                                  </div>
                                )
                              })}
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
              )
            })}
          </tbody>
        </table>
      </div>

      <div className="table-pagination-footer">
        <div className="pagination-info">Showing {showingStart} to {showingEnd} of {totalItems} transactions</div>
        <div className="pagination-controls">
          <button 
            className="page-arrow-btn" 
            onClick={handlePrevPage}
            disabled={safeCurrentPage === 1}
          >
            ‹
          </button>
          
          {getPageNumbers().map((page, index) => (
            page === '...' ? (
              <span key={`ellipsis-${index}`} className="page-ellipsis">..</span>
            ) : (
              <button 
                key={page} 
                className={`page-number-btn ${safeCurrentPage === page ? 'active' : ''}`} 
                onClick={() => handlePageClick(page)}
              >
                {page}
              </button>
            )
          ))}
          
          <button 
            className="page-arrow-btn" 
            onClick={handleNextPage}
            disabled={safeCurrentPage === totalPages}
          >
            ›
          </button>
        </div>
      </div>
    </div>
  )
}
