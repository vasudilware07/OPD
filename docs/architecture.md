# Architecture Diagram

## System Overview

```
                    +-------------------+
                    |   User Browser    |
                    |  (localhost:3000)  |
                    +--------+----------+
                             |
                    HTTP / REST API
                             |
          +------------------+------------------+
          |                                     |
+---------v-----------+           +-------------v-----------+
|   Next.js 15        |           |   FastAPI Backend        |
|   Frontend          |           |   (localhost:8000)       |
|                     |           |                         |
| - Dashboard         |   REST    | - Claims Router         |
| - Claim Submission  +<--------->+ - Members Router        |
| - Claims List       |   API     | - Policy Router         |
| - Claim Detail      |           |                         |
| - Policy Viewer     |           | +---Services----------+ |
| - Admin Dashboard   |           | | AI Engine (Gemini)  | |
+---------------------+           | | Rule Engine         | |
                                  | | Fraud Detector      | |
                                  | +---------------------+ |
                                  |                         |
                                  +----+------+-------------+
                                       |      |
                              +--------+      +--------+
                              |                        |
                     +--------v--------+     +---------v--------+
                     |   MongoDB       |     | Google Gemini    |
                     |   (port 27017)  |     | 2.0 Flash API   |
                     |                 |     |                 |
                     | - members       |     | - Multimodal    |
                     | - claims        |     | - Document OCR  |
                     | - policy        |     | - Adjudication  |
                     +-----------------+     +-----------------+
```

## Data Flow: Claim Submission

```
1. User uploads documents + fills form
           |
2. Frontend sends multipart/form-data to POST /api/claims
           |
3. Backend saves files to /uploads/{claim_id}/
           |
4. Each document sent to Gemini multimodal API for extraction
   - Patient name, doctor details, diagnosis, amounts
   - Structured JSON output
           |
5. Rule Engine runs 5-step adjudication:
   a) Eligibility check (policy status, waiting periods)
   b) Document validation (completeness, doctor reg)
   c) Coverage verification (exclusions, pre-auth)
   d) Limit validation (per-claim, annual, sub-limits, co-pay)
   e) Fraud detection (patterns, high-value)
           |
6. AI Engine runs parallel adjudication for enhanced reasoning
           |
7. Decisions merged: Rule Engine is authoritative, AI provides reasoning
           |
8. Result stored in MongoDB, response returned to frontend
           |
9. Frontend displays decision with confidence score, reasoning, rule checks
```

## Technology Choices

| Component | Choice | Why |
|-----------|--------|-----|
| Next.js 15 | Frontend | Server components, App Router, great TypeScript DX |
| FastAPI | Backend | Python ecosystem for AI, async support, auto-docs |
| MongoDB | Database | Flexible schema for varied document structures |
| Gemini 2.0 Flash | AI | Free tier, multimodal (reads images directly), fast |
| Tailwind CSS | Styling | Rapid UI development with utility classes |
| Motor | DB Driver | Async MongoDB driver for FastAPI |
