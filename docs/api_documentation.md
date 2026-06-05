# API Documentation

## Base URL
```
http://localhost:8000
```

Interactive Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Claims API

### POST /api/claims
Submit a new OPD claim with supporting documents.

**Content-Type**: `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| member_id | string | Yes | Employee ID (e.g., EMP001) |
| member_name | string | Yes | Full name of the member |
| treatment_date | string | Yes | YYYY-MM-DD format |
| claim_amount | number | Yes | Total claim amount in INR |
| hospital_name | string | No | Hospital/clinic name |
| cashless_request | boolean | No | Whether cashless is requested |
| description | string | No | Brief description |
| documents | file[] | Yes | Medical document images/PDFs |

**Response** (200):
```json
{
  "success": true,
  "message": "Claim CLM_00001 submitted and processed",
  "claim": {
    "claim_id": "CLM_00001",
    "status": "APPROVED",
    "decision": {
      "approved_amount": 1350,
      "confidence_score": 0.92,
      "reasoning": "...",
      "rule_checks": [...]
    }
  }
}
```

### GET /api/claims
List claims with optional filters.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| status | string | - | Filter by status |
| member_id | string | - | Filter by member |
| page | int | 1 | Page number |
| limit | int | 20 | Items per page |
| sort_by | string | created_at | Sort field |
| sort_order | string | desc | asc or desc |

### GET /api/claims/stats
Returns dashboard statistics (counts, amounts, rates).

### GET /api/claims/{claim_id}
Get full claim details including decision, documents, and extraction results.

### PUT /api/claims/{claim_id}/appeal
Appeal a rejected/partial claim.

**Content-Type**: `multipart/form-data`

| Field | Type | Required |
|-------|------|----------|
| reason | string | Yes |
| additional_notes | string | No |

---

## Members API

### GET /api/members
List policy members with optional search.

### GET /api/members/{member_id}
Get member details with complete claim history.

---

## Policy API

### GET /api/policy
Get current policy terms and coverage details.

### PUT /api/policy
Update policy configuration (admin). Send JSON body with fields to update.

### GET /api/policy/exclusions
List all excluded treatments/conditions.

### GET /api/policy/limits
Get coverage limits and waiting periods.
