import { useState } from 'react'
import './App.css'
import MetricsCards from './components/MetricsCards'
import FailureTypeChart from './components/FailureTypeChart'
import BeforeAfterComparison from './components/BeforeAfterComparison'
import ActionTypeChart from './components/ActionTypeChart'
import TransactionTable from './components/TransactionTable'

const API_BASE = 'http://localhost:8000'

function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [count, setCount] = useState(100)
  const [error, setError] = useState(null)

  const runRecovery = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/demo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count }),
      })
      if (!res.ok) throw new Error(`API error: ${res.status}`)
      const result = await res.json()
      setData(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>RecoverAI</h1>
        <p className="tagline">AI-Powered Payment Recovery Agent</p>
        <span className="badge">Razorpay Buildathon 2026 — Track 03</span>
      </header>

      <div className="run-section">
        <div className="count-selector">
          <label>Transactions to process:</label>
          <input
            type="number"
            value={count}
            onChange={(e) => setCount(Math.max(1, Math.min(500, parseInt(e.target.value) || 1)))}
            min="1"
            max="500"
          />
        </div>
        <br />
        <button className="run-btn" onClick={runRecovery} disabled={loading}>
          {loading && <span className="spinner" />}
          {loading ? 'Running AI Recovery Pipeline...' : 'Run Recovery Pipeline'}
        </button>
        {error && <p style={{ color: 'var(--danger)', marginTop: 12 }}>{error}</p>}
      </div>

      {loading && (
        <div className="loading-overlay">
          <div className="loader" />
          <p>Processing {count} failed transactions through the AI pipeline...</p>
          <p style={{ fontSize: '0.85rem', marginTop: 8, color: 'var(--text-muted)' }}>
            Classify → Root Cause → Strategy → Execute → Audit
          </p>
        </div>
      )}

      {!data && !loading && (
        <div className="empty-state">
          <h2>Ready to Recover Revenue</h2>
          <p>Click "Run Recovery Pipeline" to simulate failed payments and watch AI recover them in real-time.</p>
        </div>
      )}

      {data && !loading && (
        <>
          <MetricsCards metrics={data.metrics} summary={data.results_summary} />
          <BeforeAfterComparison comparison={data.before_after} />
          <div className="charts-grid">
            <FailureTypeChart data={data.metrics.by_failure_type} />
            <ActionTypeChart data={data.metrics.by_action_type} />
          </div>
          <TransactionTable results={data.sample_results} />
        </>
      )}

      <footer className="footer">
        RecoverAI &copy; 2026 — Built for Razorpay AI Buildathon | Track 03: AI Revenue Recovery
      </footer>
    </div>
  )
}

export default App
