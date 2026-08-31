import React from 'react';

export default function AuditTrail({ trail }) {
  if (!trail || trail.length === 0) {
    return <div className="text-muted">No audit trail available for this transaction.</div>;
  }

  const getStatusColor = (outcome) => {
    const out = (outcome || '').toLowerCase();
    if (out.includes('success') || out.includes('recovered')) return 'success';
    if (out.includes('block') || out.includes('fail') || out.includes('error')) return 'error';
    return 'info';
  };

  return (
    <div className="timeline">
      {trail.map((entry, idx) => {
        const statusClass = getStatusColor(entry.outcome);
        return (
          <div key={idx} className="timeline-item">
            <div className={`timeline-dot ${statusClass}`}></div>
            <div className="timeline-content">
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <strong className="text-primary">{entry.agent_name || 'System'}</strong>
                <span className="badge" style={{ backgroundColor: 'rgba(255,255,255,0.1)' }}>
                  {entry.action}
                </span>
              </div>
              <div style={{ fontSize: '0.875rem' }}>
                {entry.outcome}
              </div>
              {entry.reasoning && (
                <div className="text-muted" style={{ marginTop: '0.5rem', fontSize: '0.875rem', fontStyle: 'italic' }}>
                  "{entry.reasoning}"
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
