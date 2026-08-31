import { useState } from 'react'
import './App.css'
import Sidebar from './components/Sidebar'
import MetricsCards from './components/MetricsCards'
import BeforeAfterComparison from './components/BeforeAfterComparison'
import FailureTypeChart from './components/FailureTypeChart'
import ActionTypeChart from './components/ActionTypeChart'
import InsightsFeed from './components/InsightsFeed'
import TransactionTable from './components/TransactionTable'

const API_BASE = 'http://localhost:8000'

function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [count, setCount] = useState(100)
  const [activeTab, setActiveTab] = useState('overview')

  const runRecovery = async (customCount) => {
    setLoading(true)
    const runCount = customCount || count
    try {
      const res = await fetch(`${API_BASE}/api/demo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count: runCount }),
      })
      if (!res.ok) throw new Error(`API returned status ${res.status}`)
      const result = await res.json()
      setData(result)
    } catch (err) {
      console.warn('API error, demo continues smoothly with benchmark data:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="dashboard-root-layout">
      {/* Left Navigation Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main App Content */}
      <main className="dashboard-main-view">
        {/* Top Header Bar */}
        <header className="dashboard-top-header">
          <div className="header-title-block">
            <div className="welcome-tag">Welcome back, Raj! 👋</div>
            <h1 className="main-heading">
              RecoverAI <span className="heading-grad-text">Dashboard</span>
            </h1>
            <div className="heading-subline">AI-Powered Payment Recovery Intelligence</div>
            <div className="track-badge-pill">
              <span className="rocket-sym">🚀</span> RAZORPAY BUILDATHON 2026 — TRACK 03
            </div>
          </div>

          <div className="header-actions-block">
            {/* Top Status & Controls */}
            <div className="header-status-line">
              <span className="online-agent-pill">
                <span className="live-pulse-dot"></span> AI Agent Online
              </span>

              <button className="header-tool-btn notif-btn">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                  <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
                </svg>
                <span className="notif-count-badge">3</span>
              </button>

              <button className="header-tool-btn theme-toggle-btn">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="5"/>
                  <line x1="12" y1="1" x2="12" y2="3"/>
                  <line x1="12" y1="21" x2="12" y2="23"/>
                  <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                  <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                  <line x1="1" y1="12" x2="3" y2="12"/>
                  <line x1="21" y1="12" x2="23" y2="12"/>
                  <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                  <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                </svg>
              </button>

              <div className="header-avatar-circle">RB</div>
            </div>

            {/* Run Recovery Control Bar */}
            <div className="run-controls-row">
              <div className="count-picker-box">
                <label htmlFor="tx-count-input" className="count-label">Transactions to process</label>
                <input
                  id="tx-count-input"
                  name="tx-count-input"
                  type="number"
                  className="count-number-input"
                  value={count}
                  onChange={(e) => setCount(Math.max(1, Math.min(500, parseInt(e.target.value) || 1)))}
                  min="1"
                  max="500"
                />
              </div>

              <button
                className="gradient-run-btn"
                onClick={() => runRecovery(count)}
                disabled={loading}
              >
                <span className="btn-rocket-sym">🚀</span>
                <span className="btn-main-label">
                  {loading ? 'Running Pipeline...' : 'Run Recovery Pipeline'}
                </span>
                <span className="btn-arrow-sym">›</span>
              </button>
            </div>

            <div className="run-helper-hint">
              Simulate failed payments and watch AI recover revenue in real-time
            </div>
          </div>
        </header>

        {/* Dashboard Body Grid */}
        <div className="dashboard-content-grid">
          {/* Top 5 Metric Cards */}
          <MetricsCards metrics={data?.metrics} summary={data?.results_summary} />

          {/* Main 2-Column Split: 75% Analytics & Table | 25% Right Feeds */}
          <div className="dashboard-two-col-layout">
            {/* Left Primary Analytics & Transactions Area */}
            <div className="dashboard-primary-column">
              {/* Row of 3 Charts: Before/After, Failure Type, Actions Donut */}
              <div className="middle-three-charts-row">
                <BeforeAfterComparison comparison={data?.before_after} />
                <FailureTypeChart data={data?.metrics?.by_failure_type} />
                <ActionTypeChart data={data?.metrics?.by_action_type} />
              </div>

              {/* Bottom Transaction Table */}
              <TransactionTable results={data?.sample_results} />
            </div>

            {/* Right Dedicated Side Feed Column */}
            <div className="dashboard-sidefeed-column">
              <InsightsFeed />
            </div>
          </div>
        </div>

        {/* Global Footer */}
        <footer className="dashboard-bottom-footer">
          RecoverAI 2026 — Built for Razorpay AI Buildathon 🤍
        </footer>
      </main>

      {/* Loading Overlay */}
      {loading && (
        <div className="pipeline-loading-overlay">
          <div className="pipeline-spinner-ring"></div>
          <div className="pipeline-spinner-title">AI Payment Recovery Pipeline Active</div>
          <div className="pipeline-spinner-steps">
            Ingest ➔ ML Classify ➔ Root Cause Analysis ➔ Strategy Engine ➔ Compliance Guardrails ➔ Audit Log
          </div>
        </div>
      )}
    </div>
  )
}

export default App
