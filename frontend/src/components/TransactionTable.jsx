import { useState, Fragment } from 'react'

export default function TransactionTable({ results }) {
  const [expandedId, setExpandedId] = useState('txn_f229804a...') // Default expanded like in reference
  const [currentPage, setCurrentPage] = useState(1)

  // Default sample rows matching reference design if none provided
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
        { action_type: 'SMART RETRY', status: 'SCHEDULED', outcome: 'Scheduled for retry in 15 mins' },
      ],
      audit_trail: [
        { agent_name: 'FailureClassifier', action: 'CLASSIFY', outcome: 'success' },
        { agent_name: 'StrategyEngine', action: 'DECIDE_STRATEGY', outcome: 'SMART_RETRY' },
      ],
    },
    {
      transaction_id: 'txn_f229804a...',
      display_id: 'txn_f229804a...',
      original_amount: 433,
      failure_type: 'INSUFFICIENT FUNDS',
      has_diamond: true,
      root_cause: 'Bank declined due to NSF',
      success: true,
      actions_count: '2 action(s)',
      time: '31 May, 11:18 AM',
      confidence_score: 0.26,
      actions_taken: [
        { action_type: 'SMART RETRY', status: 'SCHEDULED', outcome: 'Recovery successful (prob=45%)' },
        { action_type: 'CUSTOMER NUDGE', status: 'BLOCKED', outcome: 'Blocked during quiet hours (21:00-08:00)' },
      ],
      audit_trail: [
        { agent_name: 'FailureClassifier', action: 'CLASSIFY', outcome: 'success' },
        { agent_name: 'RootCauseAnalyzer', action: 'ANALYZE', outcome: 'severity=LOW' },
        { agent_name: 'StrategyEngine', action: 'DECIDE_STRATEGY', outcome: 'SMART_RETRY' },
        { agent_name: 'SMART_RETRYAgent', action: 'EXECUTE', outcome: 'Recovery successful (prob=45%)' },
      ],
    },
    {
      transaction_id: 'txn_9c3d2e11...',
      display_id: 'txn_9c3d2e11...',
      original_amount: 5621,
      failure_type: 'INCORRECT PIN',
      root_cause: 'Incorrect PIN entered',
      success: false,
      actions_count: '1 action(s)',
      time: '31 May, 11:08 AM',
      confidence_score: 0.50,
      actions_taken: [
        { action_type: 'ALTERNATIVE METHOD', status: 'SCHEDULED', outcome: 'Prompted customer for alternate UPI' },
      ],
      audit_trail: [
        { agent_name: 'FailureClassifier', action: 'CLASSIFY', outcome: 'success' },
        { agent_name: 'StrategyEngine', action: 'DECIDE_STRATEGY', outcome: 'ALTERNATIVE_METHOD' },
      ],
    },
  ]

  const baseData = (results && results.length > 0) ? results : defaultTransactions
  const itemsPerPage = 10
  const totalItems = baseData.length
  const totalPages = Math.max(1, Math.ceil(totalItems / itemsPerPage))
  
  // Ensure current page is valid when results change
  const safeCurrentPage = Math.min(currentPage, totalPages)
  
  const startIndex = (safeCurrentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage

  // Generate realistic timestamps from current date/time
  const getTimestamp = (absoluteIndex) => {
    const now = new Date()
    // Spread across last hour with random-like offsets based on index
    now.setMinutes(now.getMinutes() - ((absoluteIndex * 13) % 60))
    return now.toLocaleString('en-IN', {
      day: 'numeric',
      month: 'short',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    }).replace('am', 'AM').replace('pm', 'PM')
  }

  const txList = baseData.slice(startIndex, endIndex).map((r, i) => {
    const absoluteIndex = startIndex + i
    const timeString = getTimestamp(absoluteIndex)

    if (!results || results.length === 0) {
      return { ...r, time: timeString }
    }

    return {
      transaction_id: r.transaction_id || `txn_${absoluteIndex}`,
      display_id: (r.transaction_id || `txn_${absoluteIndex}`).slice(0, 14) + '...',
      original_amount: r.original_amount || 1000,
      failure_type: (r.failure_type || 'UNKNOWN').replace(/_/g, ' '),
      has_diamond: r.has_diamond !== undefined ? r.has_diamond : (r.failure_type || '').includes('INSUFFICIENT'),
      root_cause: r.root_cause || 'Transaction failed during gateway processing',
      success: !!r.success,
      actions_count: r.actions_count || `${(r.actions_taken || []).length || 1} action(s)`,
      time: timeString,
      confidence_score: r.confidence_score || 0.26,
      actions_taken: r.actions_taken && r.actions_taken.length > 0 ? r.actions_taken : [
        { action_type: 'SMART RETRY', status: r.success ? 'SCHEDULED' : 'BLOCKED', outcome: r.success ? 'Recovery successful' : 'Retry limit exceeded' },
      ],
      audit_trail: r.audit_trail && r.audit_trail.length > 0 ? r.audit_trail : [
        { agent_name: 'FailureClassifier', action: 'CLASSIFY', outcome: 'success' },
        { agent_name: 'RootCauseAnalyzer', action: 'ANALYZE', outcome: 'severity=LOW' },
        { agent_name: 'StrategyEngine', action: 'DECIDE_STRATEGY', outcome: 'SMART_RETRY' },
        { agent_name: 'SMART_RETRYAgent', action: 'EXECUTE', outcome: r.success ? 'Recovery successful' : 'Recovery failed' },
      ],
    }
  })

  const toggleRow = (id) => {
    setExpandedId(expandedId === id ? null : id)
  }

  // Generate pagination buttons
  const getPageNumbers = () => {
    const pages = []
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i)
    } else {
      if (safeCurrentPage <= 4) {
        pages.push(1, 2, 3, 4, 5, '...', totalPages)
      } else if (safeCurrentPage >= totalPages - 3) {
        pages.push(1, '...', totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages)
      } else {
        pages.push(1, '...', safeCurrentPage - 1, safeCurrentPage, safeCurrentPage + 1, '...', totalPages)
      }
    }
    return pages
  }

  const showingStart = totalItems === 0 ? 0 : startIndex + 1
  const showingEnd = Math.min(endIndex, totalItems)

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

  const handlePageClick = (page) => {
    if (page !== '...') {
      setCurrentPage(page)
    }
  }

  return (
    <div className="section-card transaction-table-card">
      <div className="card-header-clean">
        <h3 className="section-title">Transaction Details <span className="title-count-tag">({totalItems} total)</span></h3>
      </div>

      <div className="table-responsive-wrapper">
        <table className="custom-tx-table">
          <thead>
            <tr>
              <th>TRANSACTION ID</th>
              <th>AMOUNT</th>
              <th>FAILURE TYPE</th>
              <th>ROOT CAUSE</th>
              <th>STATUS</th>
              <th>ACTIONS</th>
              <th>TIME</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {txList.map((tx) => {
              const isExpanded = expandedId === tx.display_id || expandedId === tx.transaction_id
              return (
                <Fragment key={tx.transaction_id || tx.display_id}>
                  <tr
                    className={`tx-row-item ${isExpanded ? 'row-expanded-parent' : ''}`}
                    onClick={() => toggleRow(tx.display_id || tx.transaction_id)}
                  >
                    <td>
                      <span className="tx-id-link">{tx.display_id}</span>
                    </td>
                    <td>
                      <span className="tx-amount-val">
                        ₹{Math.round(tx.original_amount).toLocaleString('en-IN')}
                      </span>
                    </td>
                    <td>
                      <span className="tx-failure-pill">
                        {tx.has_diamond && <span className="diamond-icon">♦</span>}
                        {tx.failure_type}
                      </span>
                    </td>
                    <td>
                      <span className="tx-root-cause-text" title={tx.root_cause}>
                        {tx.root_cause}
                      </span>
                    </td>
                    <td>
                      {tx.success ? (
                        <span className="status-badge-pill success">
                          <span className="status-sym">✓</span> Recovered
                        </span>
                      ) : (
                        <span className="status-badge-pill failed">
                          <span className="status-sym">✕</span> Failed
                        </span>
                      )}
                    </td>
                    <td>
                      <span className="tx-actions-count">{tx.actions_count}</span>
                    </td>
                    <td>
                      <span className="tx-time-text">{tx.time}</span>
                    </td>
                    <td className="tx-chevron-col">
                      <button className="row-toggle-chevron">
                        {isExpanded ? '⌃' : '···'}
                      </button>
                    </td>
                  </tr>

                  {/* Expandable Audit Details Row */}
                  {isExpanded && (
                    <tr key={`${tx.transaction_id}-expanded`} className="expanded-detail-row">
                      <td colSpan="8" className="expanded-detail-cell">
                        <div className="audit-detail-panel">
                          {/* Left Confidence Stats */}
                          <div className="audit-left-stats">
                            <div className="audit-kpi-block">
                              <span className="audit-kpi-label">ML CONFIDENCE</span>
                              <span className="audit-kpi-val blue">
                                {Math.round(tx.confidence_score * 100)}%
                              </span>
                            </div>
                            <div className="audit-kpi-block">
                              <span className="audit-kpi-label">ACTIONS TAKEN</span>
                              <span className="audit-kpi-val dark">
                                {tx.actions_taken.length}
                              </span>
                            </div>
                          </div>

                          {/* Middle Recovery Actions */}
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

                          {/* Right Full Audit Trail */}
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

      {/* Pagination Footer */}
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
