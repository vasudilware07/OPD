# Plum ClaimGuard — AI-Powered OPD Claim Adjudication Tool

An intelligent system that automates the adjudication of Outpatient Department (OPD) insurance claims using AI/LLM-powered document processing and rule-based decision engines.

## Features

- **AI Document Processing** — Uses Google Gemini 2.0 Flash multimodal to extract data from prescriptions, bills, and reports
- **5-Step Adjudication Engine** — Eligibility → Documents → Coverage → Limits → Medical Necessity
- **Fraud Detection** — Flags multiple same-day claims, unusual patterns, high-value claims
- **Confidence Scores** — Every decision includes an AI confidence score
- **Appeals Workflow** — Rejected/partial claims can be appealed with manual review routing
- **Admin Dashboard** — Policy configuration, analytics, member management
- **10 Test Cases** — Comprehensive test suite with expected outcomes

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS |
| Backend | FastAPI (Python), Uvicorn |
| AI/LLM | Google Gemini 2.0 Flash (multimodal) |
| Database | MongoDB + Motor (async) |
| Doc Processing | Gemini multimodal (no separate OCR needed) |

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- MongoDB running locally (port 27017)
- Google Gemini API key ([Get one free](https://aistudio.google.com/apikey))

### 1. Clone and configure

```bash
cd PLUM
# Add your Gemini API key
# Edit .env and replace your_gemini_api_key_here with your actual key
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate     # Windows
pip install -r requirements.txt

# Seed the database with sample members
python seed.py

# Generate mock medical documents
python generate_mock_docs.py

# Start the server
uvicorn main:app --reload --port 8000
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Open the app
Visit **http://localhost:3000**

## Project Structure

```
PLUM/
├── frontend/                    # Next.js 15 app
│   └── src/
│       ├── app/
│       │   ├── page.tsx         # Dashboard
│       │   ├── claims/
│       │   │   ├── page.tsx     # Claims list
│       │   │   ├── new/         # Claim submission
│       │   │   └── [id]/        # Claim detail
│       │   ├── policy/          # Policy viewer
│       │   └── admin/           # Admin dashboard
│       ├── components/          # Shared components
│       └── lib/                 # API utilities
│
├── backend/                     # FastAPI app
│   ├── main.py                  # App entry point
│   ├── seed.py                  # Database seeder
│   ├── generate_mock_docs.py    # Mock document generator
│   └── app/
│       ├── config.py            # Environment config
│       ├── database.py          # MongoDB connection
│       ├── models.py            # Pydantic schemas
│       ├── routers/
│       │   ├── claims.py        # Claims API
│       │   ├── members.py       # Members API
│       │   └── policy.py        # Policy API
│       └── services/
│           ├── ai_engine.py     # Gemini integration
│           └── rule_engine.py   # Business rules
│
├── sample_documents/            # Generated mock documents
├── policy_terms.json            # Insurance policy config
├── test_cases.json              # Test scenarios
└── docs/                        # Documentation
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/claims` | Submit new claim with documents |
| GET | `/api/claims` | List claims (filterable) |
| GET | `/api/claims/stats` | Dashboard statistics |
| GET | `/api/claims/{id}` | Claim details |
| PUT | `/api/claims/{id}/appeal` | Appeal a decision |
| GET | `/api/members` | List members |
| GET | `/api/members/{id}` | Member details |
| GET | `/api/policy` | Policy terms |
| PUT | `/api/policy` | Update policy (admin) |

Full interactive docs at: **http://localhost:8000/docs**

## Adjudication Flow

1. **Eligibility Check** — Policy active? Waiting period satisfied?
2. **Document Validation** — All required docs present? Doctor reg valid?
3. **Coverage Verification** — Treatment covered? In exclusions?
4. **Limit Validation** — Per-claim/annual limits? Sub-limits? Co-pay?
5. **Medical Necessity** — Diagnosis justifies treatment?
6. **Fraud Detection** — Suspicious patterns detected?

## Test Cases

| ID | Scenario | Expected Decision |
|----|----------|------------------|
| TC001 | Simple consultation, fever | APPROVED (₹1,350) |
| TC002 | Dental + cosmetic whitening | PARTIAL (₹8,000) |
| TC003 | Amount exceeds per-claim limit | REJECTED |
| TC004 | Missing prescription | REJECTED |
| TC005 | Diabetes within waiting period | REJECTED |
| TC006 | Ayurvedic treatment | APPROVED (₹4,000) |
| TC007 | MRI without pre-authorization | REJECTED |
| TC008 | Multiple same-day claims | MANUAL_REVIEW |
| TC009 | Weight loss (excluded) | REJECTED |
| TC010 | Network hospital cashless | APPROVED (₹3,600) |

## Assumptions

1. All member data is pre-registered (no self-registration in MVP)
2. MongoDB runs locally without authentication
3. Document images are clear enough for Gemini to process
4. Policy terms are stored as JSON and editable by admin
5. Waiting periods are calculated from member join date
6. Co-payment is 10% on all approved claims
7. Network discount is 20% for network hospitals
8. MRI and CT Scan always require pre-authorization
9. Claims below ₹500 are rejected automatically
10. Claims submitted 30+ days after treatment are late

## License

Built for the Plum AI Automation Engineer Intern Assignment.
