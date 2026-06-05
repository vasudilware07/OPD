# Assumptions

## Business Logic Assumptions

1. **Member Pre-registration**: All policy members are pre-registered in the system. No self-registration flow exists in this MVP.

2. **Policy Configuration**: A single active policy (`PLUM_OPD_2024`) applies to all members. Policy terms are stored as JSON and are editable by admin.

3. **Waiting Period Calculation**: Waiting periods are calculated from each member's `join_date`:
   - Initial waiting: 30 days for all new members
   - Pre-existing diseases: 365 days
   - Diabetes/Hypertension: 90 days
   - Joint replacement: 730 days

4. **Co-Payment**: A flat 10% co-payment is applied to all approved claims across categories.

5. **Network Discount**: 20% discount is applied for network hospitals (Apollo, Fortis, Max, Manipal, Narayana). The discount is applied before co-payment calculation.

6. **Pre-Authorization**: MRI and CT Scan always require pre-authorization. Claims for these without pre-auth are rejected.

7. **Minimum Claim**: Claims below INR 500 are automatically rejected.

8. **Submission Timeline**: Claims must be submitted within 30 days of treatment date. Late submissions are rejected.

9. **Fraud Indicators**: Claims are flagged for manual review when:
   - 2+ claims from same member on the same day
   - Claim amount exceeds INR 25,000
   - System confidence score < 70%

10. **Partial Approvals**: A claim is partially approved when some items are covered and some are excluded (e.g., root canal covered but teeth whitening is cosmetic).

## Technical Assumptions

1. **MongoDB**: Runs locally on port 27017 without authentication. Suitable for development/demo.

2. **Document Format**: Uploaded documents are images (JPEG, PNG, WebP) or PDFs. Gemini multimodal can directly process these without separate OCR.

3. **AI Accuracy**: The Gemini extraction results are used as-is. In production, a human-in-the-loop verification step would be needed.

4. **Decision Authority**: The rule engine's decision is authoritative (deterministic). The AI engine provides enhanced reasoning and confidence scoring but doesn't override the rule engine.

5. **Single Currency**: All amounts are in Indian Rupees (INR).

6. **Date Format**: Treatment dates use YYYY-MM-DD format internally, displayed as DD/MM/YYYY on documents.

7. **No Authentication**: The MVP does not include user authentication. In production, role-based access control would be needed.

8. **File Storage**: Documents are stored locally on the server filesystem. In production, cloud storage (S3, GCS) would be used.

9. **Concurrent Access**: No handling for concurrent claim submissions or race conditions on limit checks. In production, atomic operations or distributed locks would be needed.

10. **API Rate Limits**: Gemini free tier allows ~1500 requests/day. Each claim submission uses 1-3 API calls (one per document + one for adjudication).
