# 🔄 RecoverAI — Intelligent Payment Recovery Agent

> **Razorpay AI Buildathon 2026 | Track 03 — AI Revenue Recovery**

RecoverAI is an AI-powered system that **detects failed payments, diagnoses root causes, selects optimal recovery strategies, and executes automated recovery workflows** — with full audit trail and RBI compliance.

## 🎯 Problem

Indian merchants lose crores daily to failed payments. Most failures go unrecovered because:
- Manual recovery doesn't scale
- Different failure types need different interventions
- Timing and channel selection are critical but hard to optimize
- Compliance requirements make automation risky without guardrails

**RecoverAI solves this with a multi-agent AI system that recovers revenue autonomously.**

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    RecoverAI Pipeline                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Payment  │───▶│   ML Failure  │───▶│  LLM Root    │  │
│  │ Ingestion│    │  Classifier   │    │ Cause Analyzer│  │
│  └──────────┘    └──────────────┘    └──────────────┘  │
│                                            │            │
│                                            ▼            │
│                                   ┌────────────────┐    │
│                                   │   Recovery     │    │
│                                   │ Strategy Engine │    │
│                                   └────────────────┘    │
│                                            │            │
│                    ┌───────────────────────┤            │
│                    │           │           │            │
│                    ▼           ▼           ▼            │
│              ┌──────────┐ ┌────────┐ ┌──────────┐      │
│              │  Smart   │ │Customer│ │Alternative│      │
│              │  Retry   │ │ Nudge  │ │ Payment  │      │
│              │  Agent   │ │ Agent  │ │  Agent   │      │
│              └──────────┘ └────────┘ └──────────┘      │
│                    │           │           │            │
│                    └───────────┤───────────┘            │
│                                │                        │
│                    ┌───────────▼───────────┐            │
│                    │  Compliance Guardrails │            │
│                    │  + Audit Trail Logger  │            │
│                    └───────────────────────┘            │
│                                │                        │
│                    ┌───────────▼───────────┐            │
│                    │  Escalation Agent     │            │
│                    │  (Human fallback)     │            │
│                    └───────────────────────┘            │
│                                                         │
├─────────────────────────────────────────────────────────┤
│              📊 React Recovery Dashboard                 │
│         Metrics · Drill-down · Before/After             │
└─────────────────────────────────────────────────────────┘
```

## ✨ Key Features

### Multi-Agent Recovery System
- **ML Failure Classifier** — RandomForest model classifying 10+ failure types with measured precision/recall
- **LLM Root Cause Analyzer** — GPT-4/Gemini powered diagnosis explaining *why* a payment failed
- **Smart Retry Agent** — Optimal retry timing (salary days, low-traffic hours) and method selection
- **Customer Nudge Agent** — Personalized recovery messages in **English + Hinglish**
- **Alternative Payment Agent** — Intelligent payment method fallback suggestions
- **Escalation Agent** — Flags unrecoverable cases for human review with full context

### Compliance & Audit
- **Stopping Rules**: Max 3 retries, 2-hour cooldown, quiet hours (9PM-8AM), opt-out respect
- **RBI Compliance**: Mandate cooling periods, no retries on risk-blocked transactions
- **Full Audit Trail**: Every AI decision logged with agent, action, reasoning, and outcome

### Measured Results
- Batch-level recovery metrics (not cherry-picked demos)
- Before/after comparison (AI vs no-AI baseline)
- Honest exception list — reports what it *couldn't* recover and why
- Per-failure-type breakdown with precision/recall

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, SQLAlchemy |
| AI/ML | scikit-learn (classifier), OpenAI GPT-4 / Google Gemini (LLM agents) |
| Agents | LangChain / CrewAI (multi-agent orchestration) |
| Frontend | Next.js 14, Tailwind CSS, Recharts |
| Database | SQLite (development), PostgreSQL (production) |
| Payments | Razorpay Test-Mode APIs |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Razorpay Test-Mode API keys
- OpenAI API key or Google Gemini API key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env  # Edit with your API keys
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev  # Runs on http://localhost:3000
```

### Run the Pipeline

```bash
# 1. Generate synthetic failed payments
curl -X POST http://localhost:8000/api/simulate -H "Content-Type: application/json" -d '{"count": 100}'

# 2. Run recovery on all failures
curl -X POST http://localhost:8000/api/recover/batch

# 3. View metrics
curl http://localhost:8000/api/metrics

# 4. View before/after comparison
curl http://localhost:8000/api/metrics/comparison
```

## 📊 Sample Results

| Metric | Value |
|---|---|
| Total Transactions Processed | 100 |
| Failures Detected | 100 |
| Successfully Recovered | ~62 |
| **Recovery Rate** | **~62%** |
| Amount at Risk | ₹15,23,450 |
| Amount Recovered | ₹9,44,539 |
| Avg Recovery Time | 4.2 minutes |
| Escalated to Human | 12 |
| Unrecoverable | 26 |

## 📁 Project Structure

```
recoverai/
├── README.md
├── ARCHITECTURE.md
├── .env.example
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration management
│   ├── db.py                      # Database setup
│   ├── models/
│   │   └── schemas.py             # Pydantic data models
│   ├── simulator/
│   │   ├── failure_generator.py   # Synthetic failure generator
│   │   └── scenarios.py           # Failure scenario definitions
│   ├── agents/
│   │   ├── classifier.py          # ML failure classifier
│   │   ├── root_cause.py          # LLM root cause analyzer
│   │   ├── strategy_engine.py     # Recovery decision agent
│   │   ├── retry_agent.py         # Smart retry agent
│   │   ├── nudge_agent.py         # Customer nudge agent
│   │   ├── alternative_agent.py   # Alternative payment agent
│   │   └── escalation_agent.py    # Escalation agent
│   ├── compliance/
│   │   ├── guardrails.py          # Stopping rules & compliance
│   │   └── audit.py               # Audit trail logger
│   ├── pipeline/
│   │   ├── recovery_pipeline.py   # End-to-end orchestration
│   │   └── metrics.py             # Metrics collection
│   └── requirements.txt
├── frontend/
│   └── ...                        # Next.js dashboard
└── data/
    └── ...                        # Generated data & models
```

## 🔒 Compliance & Safety

- **No real payment data** — all transactions are synthetic or test-mode
- **No API keys committed** — uses .env files with .gitignore
- **Defense-only** — system recovers revenue, never processes unauthorized transactions
- **Audit everything** — every AI decision is logged and explainable
- **Stopping rules** — bounded retries, quiet hours, opt-out respect

## 📝 License

Built for the Razorpay AI Buildathon 2026.

## 👤 Author

Built with ❤️ for Track 03 — AI Revenue Recovery
