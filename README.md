# RecoverAI

RecoverAI is an autonomous payment revenue recovery engine designed for merchants on the Razorpay ecosystem. It detects failed payment attempts, classifies the root cause across 12 distinct failure patterns, and executes automated recovery actions including smart backoff retries, multi-channel customer nudges (WhatsApp, SMS, Email), and alternate payment routing while strictly respecting RBI quiet-hour guidelines.

---

## Key Capabilities

- **ML Failure Classification**: Random Forest and pattern-matching pipeline classifying failure categories with high precision.
- **Root Cause Diagnostics**: Analyzes banking gateway latencies, user balance constraints, and network timeouts to determine failure transient vs permanent status.
- **Multi-Channel Recovery**: Generates personalized 1-click retry flows across WhatsApp, SMS, and Email.
- **Razorpay SDK Integration**: Direct integration with Razorpay APIs for order generation, payment verification, and webhook ingestion.
- **RBI Compliance Engine**: Enforces quiet hours (21:00 - 08:00 IST), caps maximum retry attempts, and suppresses recovery actions on risk flags.
- **Auditing & Analytics**: Node-by-node audit ledger and merchant ROI metrics.

---

## System Architecture

```
                    ┌─────────────────────────┐
                    │     Razorpay Webhook    │
                    └────────────┬────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       RecoverAI Pipeline                        │
├─────────────────────────────────────────────────────────────────┤
│ 1. Ingest & Normalize   -> Parse gateway metadata               │
│ 2. ML Classifier        -> Categorize failure type              │
│ 3. Root Cause Engine    -> Contextual root cause diagnostic     │
│ 4. Strategy Engine      -> Smart Retry, Nudge, or Alternate Pay │
│ 5. Compliance Layer     -> RBI quiet hours & retry limits       │
│ 6. Audit & Dispatch     -> Immutable logging & action execution │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1-Click Launch (Recommended)

**Windows:**
```cmd
.\run.bat
```

**Linux / macOS:**
```bash
chmod +x run.sh
./run.sh
```

**Docker Compose:**
```bash
docker compose up --build
```

The frontend dashboard runs on `http://localhost:3000` and the API backend runs on `http://localhost:8000`.

---

### Manual Setup

#### Backend
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev -- --port 3000
```

---

## Environment Variables

Copy `.env.example` to `.env` to configure credentials:

```env
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
```

If API keys are omitted, the engine automatically operates in offline benchmark simulation mode.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/demo` | Runs benchmark recovery simulation on $N$ transactions |
| `POST` | `/api/recover/custom` | Runs diagnosis on a single transaction payload |
| `POST` | `/api/razorpay/create-order` | Generates a test order via Razorpay API |
| `POST` | `/api/webhook/razorpay` | Ingests live Razorpay webhook events |
| `POST` | `/api/webhook/simulate` | Dispatches simulated payment failure webhook |
| `GET` | `/api/metrics` | Returns aggregate recovery metrics |
| `GET` | `/api/metrics/comparison` | Returns baseline vs AI recovery lift |
| `GET` | `/api/transactions` | Lists processed transactions |
| `GET` | `/health` | Health check endpoint |

---

## License

MIT
