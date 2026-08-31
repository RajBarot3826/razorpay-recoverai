import { useState } from 'react'

export default function TransactionTable({ results }) {
  const [expandedId, setExpandedId] = useState(null)

  if (!results || results.length === 0) return null

  const toggleRow = (id) => {
    setExpandedId(expandedId === id ? null : id)
  }

  return (
    <div className="table-section">
      <h3>Transaction Details ({results.length} shown)</h3>
      <table className="tx-table">
        <thead>
          <tr>
            <th>Transaction ID</th>
            <th>Amount</th>
            <th>Failure Type</th>
            <th>Root Cause</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r) => (
            <>
              <tr key={r.transaction_id} onClick={() => toggleRow(r.transaction_id)}>
                <td>
                  <span className="tx-id">{r.transaction_id.slice(0, 16)}...</span>
                </td>
                <td style={{ fontWeight: 600 }}>
                  ₹{r.original_amount.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                </td>
                <td>
                  <span className="badge-warning">{(r.failure_type || 'UNKNOWN').replace(/_/g, ' ')}</span>
                </td>
                <td style={{ maxWidth: 280, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--text-secondary)' }}>
                  {r.root_cause || 'N/A'}
                </td>
                <td>
                  <span className={r.success ? 'badge-success' : 'badge-danger'}>
                    {r.success ? '✓ Recovered' : '✗ Failed'}
                  </span>
                </td>
                <td style={{ color: 'var(--text-muted)' }}>
                  {(r.actions_taken || []).length} action(s)
                </td>
              </tr>
              {expandedId === r.transaction_id && (
                <tr key={`${r.transaction_id}-detail`}>
                  <td colSpan={6} style={{ padding: 0 }}>
                    <AuditTrail
                      actions={r.actions_taken || []}
                      auditTrail={r.audit_trail || []}
                      confidence={r.confidence_score}
                    />
                  </td>
                </tr>
              )}
            </>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function AuditTrail({ actions, auditTrail, confidence }) {
  return (
    <div className="audit-trail">
      <div style={{ display: 'flex', gap: 32, marginBottom: 16, flexWrap: 'wrap' }}>
        <div>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>ML CONFIDENCE</span>
          <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent)' }}>
            {(confidence * 100).toFixed(0)}%
          </div>
        </div>
        <div>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>ACTIONS TAKEN</span>
          <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            {actions.length}
          </div>
        </div>
      </div>

      {actions.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 1 }}>
            Recovery Actions
          </div>
          {actions.map((a, i) => (
            <div key={i} style={{
              display: 'flex', gap: 12, padding: '8px 0',
              borderLeft: `2px solid ${a.status === 'BLOCKED' ? 'var(--danger)' : a.status === 'COMPLETED' || a.status === 'SCHEDULED' ? 'var(--success)' : 'var(--accent)'}`,
              paddingLeft: 16, marginLeft: 8, marginBottom: 4
            }}>
              <span style={{ color: 'var(--accent)', fontWeight: 600, fontSize: '0.85rem', minWidth: 140 }}>
                {(a.action_type || '').replace(/_/g, ' ')}
              </span>
              <span className={a.status === 'BLOCKED' ? 'badge-danger' : a.status === 'COMPLETED' || a.status === 'SCHEDULED' ? 'badge-success' : 'badge-warning'} style={{ fontSize: '0.75rem' }}>
                {a.status}
              </span>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', flex: 1 }}>
                {a.outcome || (typeof a.details === 'string' ? a.details : JSON.stringify(a.details))}
              </span>
            </div>
          ))}
        </div>
      )}

      {auditTrail.length > 0 && (
        <div>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 1 }}>
            Full Audit Trail
          </div>
          {auditTrail.map((e, i) => {
            const isBlocked = (e.outcome || '').toLowerCase().includes('blocked')
            const isSuccess = (e.outcome || '').toLowerCase().includes('success')
            return (
              <div key={i} className={`audit-entry ${isBlocked ? 'blocked' : isSuccess ? 'success' : 'info'}`}>
                <span className="audit-agent">{e.agent_name}</span>
                <span className="audit-action">{e.action}</span>
                <span className="audit-outcome">{e.outcome}</span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
