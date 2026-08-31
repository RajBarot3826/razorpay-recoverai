import { useState } from 'react'

export default function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: '🏠' },
    { id: 'sandbox', label: 'AI Sandbox', icon: '🧪', badge: 'LIVE' },
    { id: 'transactions', label: 'Transactions', icon: '📑' },
    { id: 'pipeline', label: 'Recovery Pipeline', icon: '🔄' },
    { id: 'analytics', label: 'Analytics', icon: '📊' },
    { id: 'customers', label: 'Customers', icon: '👥' },
    { id: 'insights', label: 'Insights', icon: '💡' },
    { id: 'alerts', label: 'Alerts', icon: '🔔', badge: '4' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
  ]

  return (
    <aside className="sidebar">
      {/* Brand Logo */}
      <div className="sidebar-logo">
        <div className="logo-icon-wrap">
          <div className="logo-sparkle">✦</div>
          <div className="logo-icon-svg">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="url(#logo-grad)" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="url(#logo-grad)" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="url(#logo-grad)" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
              <defs>
                <linearGradient id="logo-grad" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#38bdf8"/>
                  <stop offset="0.5" stopColor="#3b82f6"/>
                  <stop offset="1" stopColor="#8b5cf6"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
        </div>
        <div className="logo-text">
          <span className="brand-name">Recover<span className="brand-highlight">AI</span></span>
          <span className="brand-subtitle">AI Payment Recovery Agent</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
            onClick={() => setActiveTab(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
            {item.badge && <span className="nav-badge-pill">{item.badge}</span>}
          </button>
        ))}
      </nav>

      {/* AI Engine Status Card with 3D Animated Bot */}
      <div className="sidebar-ai-card">
        <div className="ai-card-header">
          <span className="ai-status-title">AI Engine Status</span>
          <span className="ai-active-indicator">
            <span className="pulse-dot"></span> Active
          </span>
        </div>

        <div className="ai-gauge-container">
          <svg className="gauge-svg" viewBox="0 0 100 100">
            {/* Background Track */}
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="#e2e8f0"
              strokeWidth="6"
            />
            {/* Animated Gauge Arc */}
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="url(#gauge-grad)"
              strokeWidth="6"
              strokeDasharray="251.2"
              strokeDashoffset="10"
              strokeLinecap="round"
              transform="rotate(-90 50 50)"
            />
            <defs>
              <linearGradient id="gauge-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#06b6d4" />
                <stop offset="50%" stopColor="#3b82f6" />
                <stop offset="100%" stopColor="#10b981" />
              </linearGradient>
            </defs>
          </svg>

          {/* 3D Cute Robot Icon in Center */}
          <div className="ai-bot-avatar">
            <div className="bot-head">
              <div className="bot-antenna"></div>
              <div className="bot-face">
                <div className="bot-eyes">
                  <span className="bot-eye left"></span>
                  <span className="bot-eye right"></span>
                </div>
                <div className="bot-mouth"></div>
              </div>
            </div>
          </div>
        </div>

        <div className="ai-metrics-text">
          <div className="ai-accuracy-val">98.6%</div>
          <div className="ai-accuracy-label">Model Accuracy</div>
          <div className="ai-accuracy-trend">
            <span className="trend-arrow">↑</span> 28.5% vs last 7 days
          </div>
        </div>
      </div>

      {/* User Profile */}
      <div className="sidebar-user-card">
        <div className="user-avatar-wrap">
          <div className="user-avatar-circle">
            <span>RB</span>
          </div>
        </div>
        <div className="user-meta">
          <div className="user-name">Raj Barot</div>
          <div className="user-role">Developer</div>
        </div>
        <div className="user-chevron">⌄</div>
      </div>
    </aside>
  )
}
