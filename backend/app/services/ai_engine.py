"""
AI Engine — Google Gemini integration for document extraction and adjudication.
Uses multimodal capabilities to directly process medical document images/PDFs.
"""
import json
import base64
import os
import traceback
from typing import List, Optional
import google.generativeai as genai
from app.config import GEMINI_API_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Use Gemini 2.0 Flash for speed and multimodal support
model = genai.GenerativeModel("gemini-2.0-flash")


EXTRACTION_PROMPT = """You are a medical document data extraction AI specializing in Indian healthcare documents.
Analyze this medical document image and extract ALL information you can find.

Return ONLY a valid JSON object (no markdown, no code blocks) with these fields:
{
  "document_type": "prescription|bill|diagnostic_report|pharmacy_bill|other",
  "patient_name": "string or null",
  "patient_age": "string or null",
  "patient_gender": "string or null",
  "doctor_name": "string or null",
  "doctor_registration": "string or null (format: STATE/NUMBER/YEAR)",
  "doctor_qualification": "string or null",
  "clinic_name": "string or null",
  "clinic_address": "string or null",
  "treatment_date": "YYYY-MM-DD or null",
  "diagnosis": "string or null",
  "chief_complaints": ["symptom1", "symptom2"],
  "medicines_prescribed": [
    {"name": "string", "dosage": "string", "duration": "string", "quantity": 0}
  ],
  "tests_prescribed": ["test1", "test2"],
  "tests_results": [
    {"test_name": "string", "result": "string", "normal_range": "string"}
  ],
  "procedures": ["procedure1"],
  "bill_items": [
    {"description": "string", "amount": 0, "category": "consultation|diagnostic|pharmacy|procedure|other"}
  ],
  "total_amount": 0,
  "payment_mode": "string or null",
  "gst_number": "string or null",
  "bill_number": "string or null",
  "confidence": 0.95,
  "notes": "any observations about document quality, missing fields, or concerns"
}

Important rules:
- If a field is not visible or unclear, set it to null
- For amounts, extract numerical values only (no ₹ symbol)
- Doctor registration numbers in India follow format: STATE_CODE/NUMBER/YEAR (e.g., KA/45678/2015)
- Detect if document appears to be modified or tampered with
- Note any inconsistencies between patient details across documents
- If the image is blurry or illegible, note it in the notes field and reduce confidence score
"""


ADJUDICATION_PROMPT_TEMPLATE = """You are an expert insurance claim adjudicator for Indian OPD (Outpatient Department) claims.

POLICY TERMS:
{policy_terms}

EXTRACTED CLAIM DATA:
{claim_data}

MEMBER INFORMATION:
{member_info}

CLAIM HISTORY:
{claim_history}

Based on the above information, evaluate this OPD claim through these steps:

1. ELIGIBILITY CHECK:
   - Is the policy active on the treatment date?
   - Has the initial waiting period (30 days) been satisfied?
   - Check specific waiting periods for pre-existing conditions (diabetes: 90 days, hypertension: 90 days)
   - Is the member covered under the policy?

2. DOCUMENT VALIDATION:
   - Are all required documents present (prescription, bills)?
   - Is the doctor's registration number valid?
   - Do dates match across documents?
   - Do patient details match member records?

3. COVERAGE VERIFICATION:
   - Is the treatment/service covered?
   - Is it in the exclusions list?
   - Does it require pre-authorization?
   - Check: cosmetic procedures, weight loss, experimental treatments

4. LIMIT VALIDATION:
   - Per-claim limit: ₹5,000
   - Annual limit: ₹50,000
   - Sub-limits by category (consultation: ₹2,000, diagnostics: ₹10,000, pharmacy: ₹15,000, dental: ₹10,000, vision: ₹5,000, alternative medicine: ₹8,000)
   - Calculate co-payment (10% for consultation)
   - Network discount (20% for network hospitals)

5. MEDICAL NECESSITY:
   - Does the diagnosis justify the treatment?
   - Are prescribed medicines appropriate for the diagnosis?
   - Are the tests relevant to the condition?

6. FRAUD INDICATORS:
   - Multiple claims on same day
   - Unusually high amounts
   - Suspicious patterns
   - Modified documents

Return ONLY a valid JSON object (no markdown, no code blocks):
{{
  "decision": "APPROVED|REJECTED|PARTIAL|MANUAL_REVIEW",
  "approved_amount": 0,
  "rejected_amount": 0,
  "rejection_reasons": ["REASON_CODE1"],
  "rejected_items": ["description of rejected items"],
  "deductions": {{
    "copay": 0,
    "network_discount": 0,
    "sub_limit_adjustment": 0
  }},
  "confidence_score": 0.95,
  "reasoning": "Detailed explanation of the decision",
  "notes": "Additional observations",
  "next_steps": "What the claimant should do next",
  "fraud_flags": [],
  "cashless_approved": false,
  "network_discount": 0,
  "rule_checks": [
    {{"rule": "Eligibility", "status": "PASS|FAIL", "detail": "explanation"}},
    {{"rule": "Documents", "status": "PASS|FAIL", "detail": "explanation"}},
    {{"rule": "Coverage", "status": "PASS|FAIL", "detail": "explanation"}},
    {{"rule": "Limits", "status": "PASS|FAIL", "detail": "explanation"}},
    {{"rule": "Medical Necessity", "status": "PASS|FAIL", "detail": "explanation"}},
    {{"rule": "Fraud Check", "status": "PASS|FAIL", "detail": "explanation"}}
  ]
}}

Valid rejection reason codes:
POLICY_INACTIVE, WAITING_PERIOD, MEMBER_NOT_COVERED, MISSING_DOCUMENTS,
ILLEGIBLE_DOCUMENTS, INVALID_PRESCRIPTION, DOCTOR_REG_INVALID, DATE_MISMATCH,
PATIENT_MISMATCH, SERVICE_NOT_COVERED, EXCLUDED_CONDITION, PRE_AUTH_MISSING,
ANNUAL_LIMIT_EXCEEDED, SUB_LIMIT_EXCEEDED, PER_CLAIM_EXCEEDED,
NOT_MEDICALLY_NECESSARY, EXPERIMENTAL_TREATMENT, COSMETIC_PROCEDURE,
LATE_SUBMISSION, DUPLICATE_CLAIM, BELOW_MIN_AMOUNT
"""


def _clean_json_response(text: str) -> str:
    """Strip markdown code fences and other wrappers from the LLM response."""
    text = text.strip()
    if text.startswith("```"):
        # Remove opening fence (```json or ```)
        first_newline = text.index("\n")
        text = text[first_newline + 1:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


async def extract_document_data(file_path: str, file_content: bytes, mime_type: str) -> dict:
    """
    Use Gemini's multimodal capabilities to extract structured data from a medical document.
    Accepts images (JPEG, PNG) and PDFs.
    """
    try:
        # Build the content parts for Gemini
        image_part = {
            "mime_type": mime_type,
            "data": base64.b64encode(file_content).decode("utf-8")
        }

        response = model.generate_content(
            [EXTRACTION_PROMPT, image_part],
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=4096,
            )
        )

        # Parse the JSON response
        result_text = _clean_json_response(response.text)
        result = json.loads(result_text)
        return result

    except json.JSONDecodeError as e:
        print(f"⚠️ JSON parse error from Gemini: {e}")
        print(f"Raw response: {response.text[:500]}")
        return {
            "error": "Failed to parse extraction result",
            "raw_text": response.text[:1000],
            "confidence": 0.0,
            "notes": "AI extraction returned unparseable response"
        }
    except Exception as e:
        print(f"❌ Gemini extraction error: {traceback.format_exc()}")
        return {
            "error": str(e),
            "confidence": 0.0,
            "notes": f"AI extraction failed: {str(e)}"
        }


async def adjudicate_claim(
    claim_data: dict,
    extraction_results: List[dict],
    member_info: dict,
    policy_terms: dict,
    claim_history: List[dict]
) -> dict:
    """
    Use Gemini to make an intelligent adjudication decision based on
    extracted data, policy terms, and claim history.
    """
    try:
        prompt = ADJUDICATION_PROMPT_TEMPLATE.format(
            policy_terms=json.dumps(policy_terms, indent=2),
            claim_data=json.dumps({
                "claim_amount": claim_data.get("claim_amount", 0),
                "treatment_date": claim_data.get("treatment_date", ""),
                "hospital_name": claim_data.get("hospital_name", ""),
                "cashless_request": claim_data.get("cashless_request", False),
                "description": claim_data.get("description", ""),
                "extracted_documents": extraction_results
            }, indent=2),
            member_info=json.dumps(member_info, indent=2),
            claim_history=json.dumps(claim_history, indent=2)
        )

        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=4096,
            )
        )

        result_text = _clean_json_response(response.text)
        result = json.loads(result_text)
        return result

    except json.JSONDecodeError as e:
        print(f"⚠️ Adjudication JSON parse error: {e}")
        return {
            "decision": "MANUAL_REVIEW",
            "approved_amount": 0,
            "confidence_score": 0.3,
            "reasoning": "AI adjudication returned unparseable response, sending to manual review",
            "notes": f"Parse error: {str(e)}",
            "next_steps": "This claim will be reviewed by a human adjudicator",
            "fraud_flags": [],
            "rejection_reasons": [],
            "rule_checks": []
        }
    except Exception as e:
        print(f"❌ Adjudication error: {traceback.format_exc()}")
        return {
            "decision": "MANUAL_REVIEW",
            "approved_amount": 0,
            "confidence_score": 0.0,
            "reasoning": f"AI adjudication failed: {str(e)}",
            "notes": "Automatically routed to manual review due to system error",
            "next_steps": "This claim will be reviewed by a human adjudicator",
            "fraud_flags": [],
            "rejection_reasons": [],
            "rule_checks": []
        }


async def evaluate_medical_necessity(diagnosis: str, treatments: List[str], medicines: List[str]) -> dict:
    """Evaluate if the treatment is medically necessary for the given diagnosis."""
    try:
        prompt = f"""As a medical insurance expert, evaluate if the following treatments are medically
necessary for the given diagnosis.

Diagnosis: {diagnosis}
Treatments/Procedures: {json.dumps(treatments)}
Medicines: {json.dumps(medicines)}

Return ONLY a valid JSON object (no markdown):
{{
  "is_necessary": true/false,
  "confidence": 0.95,
  "reasoning": "explanation",
  "flagged_items": ["items that seem unnecessary"],
  "alignment_score": 0.9
}}"""

        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(temperature=0.1, max_output_tokens=1024)
        )

        result_text = _clean_json_response(response.text)
        return json.loads(result_text)

    except Exception as e:
        return {
            "is_necessary": True,
            "confidence": 0.5,
            "reasoning": f"Could not evaluate: {str(e)}",
            "flagged_items": [],
            "alignment_score": 0.5
        }
