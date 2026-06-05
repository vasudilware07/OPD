"""
Rule Engine — Deterministic rule-based adjudication logic.
Implements the 5-step adjudication flow as a fallback/supplement to AI.
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Optional, Tuple


def load_policy_terms() -> dict:
    """Load policy terms from the JSON file."""
    policy_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "policy_terms.json")
    with open(policy_path, "r") as f:
        return json.load(f)


def check_eligibility(member: dict, treatment_date: str, policy: dict) -> Tuple[bool, List[str], List[dict]]:
    """
    Step 1: Basic eligibility check.
    Returns (is_eligible, rejection_reasons, rule_checks)
    """
    reasons = []
    checks = []
    treatment_dt = datetime.strptime(treatment_date, "%Y-%m-%d")

    # Check policy status
    policy_start = datetime.strptime(policy.get("effective_date", "2024-01-01"), "%Y-%m-%d")
    if member.get("policy_status", "active") != "active":
        reasons.append("POLICY_INACTIVE")
        checks.append({"rule": "Policy Status", "status": "FAIL", "detail": "Policy is not active"})
    else:
        checks.append({"rule": "Policy Status", "status": "PASS", "detail": "Policy is active"})

    # Check initial waiting period (30 days)
    join_date = datetime.strptime(member.get("join_date", "2024-01-01"), "%Y-%m-%d")
    initial_waiting = policy.get("waiting_periods", {}).get("initial_waiting", 30)
    eligible_from = join_date + timedelta(days=initial_waiting)

    if treatment_dt < eligible_from:
        reasons.append("WAITING_PERIOD")
        checks.append({
            "rule": "Initial Waiting Period",
            "status": "FAIL",
            "detail": f"Initial waiting period of {initial_waiting} days not satisfied. Eligible from {eligible_from.strftime('%Y-%m-%d')}"
        })
    else:
        checks.append({"rule": "Initial Waiting Period", "status": "PASS", "detail": "Waiting period satisfied"})

    return len(reasons) == 0, reasons, checks


def check_specific_waiting_period(member: dict, treatment_date: str, diagnosis: str, policy: dict) -> Tuple[bool, List[str], List[dict]]:
    """Check waiting periods for specific conditions (diabetes, hypertension, etc.)."""
    reasons = []
    checks = []
    treatment_dt = datetime.strptime(treatment_date, "%Y-%m-%d")
    join_date = datetime.strptime(member.get("join_date", "2024-01-01"), "%Y-%m-%d")

    specific_ailments = policy.get("waiting_periods", {}).get("specific_ailments", {})
    diagnosis_lower = (diagnosis or "").lower()

    for ailment, days in specific_ailments.items():
        if ailment.lower() in diagnosis_lower:
            eligible_from = join_date + timedelta(days=days)
            if treatment_dt < eligible_from:
                reasons.append("WAITING_PERIOD")
                checks.append({
                    "rule": f"Specific Waiting Period ({ailment})",
                    "status": "FAIL",
                    "detail": f"{ailment.title()} has {days}-day waiting period. Eligible from {eligible_from.strftime('%Y-%m-%d')}"
                })
            else:
                checks.append({
                    "rule": f"Specific Waiting Period ({ailment})",
                    "status": "PASS",
                    "detail": f"Waiting period for {ailment} satisfied"
                })

    return len(reasons) == 0, reasons, checks


def check_documents(extraction_results: List[dict]) -> Tuple[bool, List[str], List[dict]]:
    """
    Step 2: Document validation.
    Checks for presence, validity, and consistency.
    """
    reasons = []
    checks = []

    if not extraction_results:
        reasons.append("MISSING_DOCUMENTS")
        checks.append({"rule": "Document Presence", "status": "FAIL", "detail": "No documents submitted"})
        return False, reasons, checks

    has_prescription = False
    has_bill = False
    doctor_reg_found = False

    for doc in extraction_results:
        doc_type = doc.get("document_type", "other")
        if doc_type == "prescription":
            has_prescription = True
            if doc.get("doctor_registration"):
                doctor_reg_found = True
        elif doc_type in ("bill", "pharmacy_bill"):
            has_bill = True

    if not has_prescription:
        reasons.append("MISSING_DOCUMENTS")
        checks.append({"rule": "Prescription", "status": "FAIL", "detail": "Prescription from registered doctor is required"})
    else:
        checks.append({"rule": "Prescription", "status": "PASS", "detail": "Prescription found"})

    if not has_bill:
        reasons.append("MISSING_DOCUMENTS")
        checks.append({"rule": "Bill/Invoice", "status": "FAIL", "detail": "Bill or invoice is required"})
    else:
        checks.append({"rule": "Bill/Invoice", "status": "PASS", "detail": "Bill found"})

    if has_prescription and not doctor_reg_found:
        reasons.append("DOCTOR_REG_INVALID")
        checks.append({"rule": "Doctor Registration", "status": "FAIL", "detail": "Doctor registration number not found on prescription"})
    elif has_prescription:
        checks.append({"rule": "Doctor Registration", "status": "PASS", "detail": "Doctor registration number found"})

    # Check document confidence
    for doc in extraction_results:
        if doc.get("confidence", 1.0) < 0.5:
            reasons.append("ILLEGIBLE_DOCUMENTS")
            checks.append({"rule": "Document Legibility", "status": "FAIL", "detail": "Document quality is too low to process"})
            break

    return len(reasons) == 0, reasons, checks


def check_coverage(diagnosis: str, treatments: List[str], policy: dict) -> Tuple[bool, List[str], List[str], List[dict]]:
    """
    Step 3: Coverage verification.
    Returns (is_covered, rejection_reasons, rejected_items, rule_checks)
    """
    reasons = []
    rejected_items = []
    checks = []
    exclusions = [e.lower() for e in policy.get("exclusions", [])]
    diagnosis_lower = (diagnosis or "").lower()

    # Check exclusions
    for exclusion in exclusions:
        if any(keyword in diagnosis_lower for keyword in exclusion.split()):
            if "weight loss" in exclusion and ("obesity" in diagnosis_lower or "weight" in diagnosis_lower or "bmi" in diagnosis_lower):
                reasons.append("SERVICE_NOT_COVERED")
                rejected_items.append(f"Weight loss treatment - excluded from coverage")
                checks.append({"rule": "Exclusion Check", "status": "FAIL", "detail": f"Excluded: {exclusion}"})
            elif "cosmetic" in exclusion and "cosmetic" in diagnosis_lower:
                reasons.append("COSMETIC_PROCEDURE")
                rejected_items.append("Cosmetic procedure - excluded from coverage")
                checks.append({"rule": "Exclusion Check", "status": "FAIL", "detail": f"Excluded: {exclusion}"})
            elif "infertility" in exclusion and "infertility" in diagnosis_lower:
                reasons.append("EXCLUDED_CONDITION")
                checks.append({"rule": "Exclusion Check", "status": "FAIL", "detail": f"Excluded: {exclusion}"})
            elif "experimental" in exclusion and "experimental" in diagnosis_lower:
                reasons.append("EXPERIMENTAL_TREATMENT")
                checks.append({"rule": "Exclusion Check", "status": "FAIL", "detail": f"Excluded: {exclusion}"})

    # Check for cosmetic procedures in treatments
    for treatment in treatments:
        treatment_lower = treatment.lower()
        if any(kw in treatment_lower for kw in ["whitening", "cosmetic", "botox", "liposuction", "hair transplant"]):
            if "COSMETIC_PROCEDURE" not in reasons:
                reasons.append("COSMETIC_PROCEDURE")
            rejected_items.append(f"{treatment} - cosmetic procedure excluded")
            checks.append({"rule": f"Treatment Coverage ({treatment})", "status": "FAIL", "detail": "Cosmetic procedure"})
        elif any(kw in treatment_lower for kw in ["weight loss", "bariatric", "diet plan"]):
            if "SERVICE_NOT_COVERED" not in reasons:
                reasons.append("SERVICE_NOT_COVERED")
            rejected_items.append(f"{treatment} - weight loss treatment excluded")
            checks.append({"rule": f"Treatment Coverage ({treatment})", "status": "FAIL", "detail": "Weight loss treatment excluded"})

    # Check MRI/CT pre-authorization
    for treatment in treatments:
        treatment_lower = treatment.lower()
        if "mri" in treatment_lower or "ct scan" in treatment_lower:
            reasons.append("PRE_AUTH_MISSING")
            checks.append({
                "rule": "Pre-Authorization",
                "status": "FAIL",
                "detail": f"{treatment} requires pre-authorization"
            })

    if not reasons:
        checks.append({"rule": "Coverage Check", "status": "PASS", "detail": "Treatment is covered under policy"})

    return len(reasons) == 0, reasons, rejected_items, checks


def check_limits(claim_amount: float, category: str, claims_ytd: float, policy: dict) -> Tuple[bool, float, dict, List[str], List[dict]]:
    """
    Step 4: Limit validation.
    Returns (within_limits, approved_amount, deductions, rejection_reasons, rule_checks)
    """
    reasons = []
    checks = []
    deductions = {}
    coverage = policy.get("coverage_details", {})
    per_claim_limit = coverage.get("per_claim_limit", 5000)
    annual_limit = coverage.get("annual_limit", 50000)
    approved = claim_amount

    # Per-claim limit
    if claim_amount > per_claim_limit:
        reasons.append("PER_CLAIM_EXCEEDED")
        checks.append({
            "rule": "Per-Claim Limit",
            "status": "FAIL",
            "detail": f"Claim ₹{claim_amount} exceeds per-claim limit of ₹{per_claim_limit}"
        })
        return False, 0, deductions, reasons, checks
    else:
        checks.append({"rule": "Per-Claim Limit", "status": "PASS", "detail": f"₹{claim_amount} within ₹{per_claim_limit} limit"})

    # Annual limit
    if claims_ytd + claim_amount > annual_limit:
        remaining = annual_limit - claims_ytd
        if remaining <= 0:
            reasons.append("ANNUAL_LIMIT_EXCEEDED")
            checks.append({"rule": "Annual Limit", "status": "FAIL", "detail": f"Annual limit of ₹{annual_limit} exhausted"})
            return False, 0, deductions, reasons, checks
        else:
            approved = min(approved, remaining)
            checks.append({"rule": "Annual Limit", "status": "PASS", "detail": f"Remaining annual limit: ₹{remaining}"})
    else:
        checks.append({"rule": "Annual Limit", "status": "PASS", "detail": f"Within annual limit (₹{claims_ytd + claim_amount}/₹{annual_limit})"})

    # Sub-limits by category
    sub_limit_map = {
        "consultation": coverage.get("consultation_fees", {}).get("sub_limit", 2000),
        "diagnostic": coverage.get("diagnostic_tests", {}).get("sub_limit", 10000),
        "pharmacy": coverage.get("pharmacy", {}).get("sub_limit", 15000),
        "dental": coverage.get("dental", {}).get("sub_limit", 10000),
        "vision": coverage.get("vision", {}).get("sub_limit", 5000),
        "alternative_medicine": coverage.get("alternative_medicine", {}).get("sub_limit", 8000),
    }

    if category in sub_limit_map and claim_amount > sub_limit_map[category]:
        sub_limit = sub_limit_map[category]
        approved = min(approved, sub_limit)
        deductions["sub_limit_adjustment"] = claim_amount - sub_limit
        checks.append({
            "rule": f"Sub-Limit ({category})",
            "status": "PASS",
            "detail": f"Adjusted to sub-limit ₹{sub_limit}"
        })

    # Co-payment calculation
    copay_pct = coverage.get("consultation_fees", {}).get("copay_percentage", 10)
    copay_amount = round(approved * copay_pct / 100, 2)
    approved = round(approved - copay_amount, 2)
    deductions["copay"] = copay_amount
    checks.append({"rule": "Co-Payment", "status": "PASS", "detail": f"{copay_pct}% co-pay = ₹{copay_amount}"})

    return True, approved, deductions, reasons, checks


def check_network_discount(hospital_name: str, claim_amount: float, policy: dict) -> Tuple[float, bool]:
    """Check if hospital is in network and apply discount."""
    network_hospitals = [h.lower() for h in policy.get("network_hospitals", [])]
    if hospital_name and hospital_name.lower() in network_hospitals:
        discount_pct = policy.get("coverage_details", {}).get("consultation_fees", {}).get("network_discount", 20)
        discount = round(claim_amount * discount_pct / 100, 2)
        return discount, True
    return 0, False


def check_fraud_indicators(claim_data: dict, claim_history: List[dict]) -> Tuple[bool, List[str], List[dict]]:
    """
    Step 6: Fraud detection.
    Check for suspicious patterns.
    """
    flags = []
    checks = []
    treatment_date = claim_data.get("treatment_date", "")

    # Multiple claims on same day
    same_day_claims = [c for c in claim_history if c.get("treatment_date") == treatment_date]
    if len(same_day_claims) >= 2:
        flags.append("Multiple claims on same day")

    # High claim frequency (more than 5 in last 30 days)
    if len(claim_history) >= 5:
        flags.append("High claim frequency detected")

    # High-value claim
    if claim_data.get("claim_amount", 0) > 25000:
        flags.append("High-value claim exceeding ₹25,000")

    # Explicit previous_claims_same_day field
    if claim_data.get("previous_claims_same_day", 0) >= 2:
        flags.append("Multiple claims on same day")
        flags.append("Unusual pattern detected")

    if flags:
        checks.append({"rule": "Fraud Detection", "status": "FAIL", "detail": f"Flags: {', '.join(flags)}"})
    else:
        checks.append({"rule": "Fraud Detection", "status": "PASS", "detail": "No fraud indicators detected"})

    return len(flags) == 0, flags, checks


def check_submission_timeline(treatment_date: str, submission_date: str, policy: dict) -> Tuple[bool, List[str], List[dict]]:
    """Check if claim was submitted within the allowed timeline."""
    reasons = []
    checks = []
    max_days = policy.get("claim_requirements", {}).get("submission_timeline_days", 30)

    treatment_dt = datetime.strptime(treatment_date, "%Y-%m-%d")
    submission_dt = datetime.strptime(submission_date, "%Y-%m-%d")
    days_diff = (submission_dt - treatment_dt).days

    if days_diff > max_days:
        reasons.append("LATE_SUBMISSION")
        checks.append({
            "rule": "Submission Timeline",
            "status": "FAIL",
            "detail": f"Submitted {days_diff} days after treatment (max: {max_days} days)"
        })
    else:
        checks.append({"rule": "Submission Timeline", "status": "PASS", "detail": f"Submitted within {max_days}-day window"})

    return len(reasons) == 0, reasons, checks


def check_minimum_amount(claim_amount: float, policy: dict) -> Tuple[bool, List[str], List[dict]]:
    """Check if claim meets minimum amount requirement."""
    reasons = []
    checks = []
    min_amount = policy.get("claim_requirements", {}).get("minimum_claim_amount", 500)

    if claim_amount < min_amount:
        reasons.append("BELOW_MIN_AMOUNT")
        checks.append({
            "rule": "Minimum Claim Amount",
            "status": "FAIL",
            "detail": f"Claim ₹{claim_amount} is below minimum ₹{min_amount}"
        })
    else:
        checks.append({"rule": "Minimum Claim Amount", "status": "PASS", "detail": f"Meets minimum ₹{min_amount}"})

    return len(reasons) == 0, reasons, checks


def run_rule_engine(
    claim_data: dict,
    extraction_results: List[dict],
    member: dict,
    claim_history: List[dict]
) -> dict:
    """
    Run the complete rule engine against a claim.
    Returns a structured decision similar to the AI engine output.
    """
    policy = load_policy_terms()
    all_reasons = []
    all_checks = []
    all_rejected_items = []
    all_fraud_flags = []

    treatment_date = claim_data.get("treatment_date", datetime.now().strftime("%Y-%m-%d"))
    claim_amount = claim_data.get("claim_amount", 0)
    submission_date = datetime.now().strftime("%Y-%m-%d")

    # Determine diagnosis and treatments from extraction
    diagnosis = ""
    treatments = []
    medicines = []
    for doc in extraction_results:
        if doc.get("diagnosis"):
            diagnosis = doc["diagnosis"]
        treatments.extend(doc.get("procedures", []))
        treatments.extend(doc.get("tests_prescribed", []))
        for med in doc.get("medicines_prescribed", []):
            if isinstance(med, dict):
                medicines.append(med.get("name", ""))
            else:
                medicines.append(str(med))

    # Step 0: Minimum amount
    ok, reasons, checks = check_minimum_amount(claim_amount, policy)
    all_reasons.extend(reasons)
    all_checks.extend(checks)

    # Step 1: Eligibility
    ok, reasons, checks = check_eligibility(member, treatment_date, policy)
    all_reasons.extend(reasons)
    all_checks.extend(checks)

    # Specific waiting periods
    ok, reasons, checks = check_specific_waiting_period(member, treatment_date, diagnosis, policy)
    all_reasons.extend(reasons)
    all_checks.extend(checks)

    # Step 2: Document validation
    ok, reasons, checks = check_documents(extraction_results)
    all_reasons.extend(reasons)
    all_checks.extend(checks)

    # Step 3: Coverage
    ok, reasons, rejected_items, checks = check_coverage(diagnosis, treatments, policy)
    all_reasons.extend(reasons)
    all_rejected_items.extend(rejected_items)
    all_checks.extend(checks)

    # Step 4: Limits
    category = determine_category(extraction_results)
    claims_ytd = sum(c.get("approved_amount", 0) for c in claim_history)
    limits_ok, approved_amount, deductions, reasons, checks = check_limits(claim_amount, category, claims_ytd, policy)
    all_reasons.extend(reasons)
    all_checks.extend(checks)

    # Step 5: Submission timeline
    ok, reasons, checks = check_submission_timeline(treatment_date, submission_date, policy)
    all_reasons.extend(reasons)
    all_checks.extend(checks)

    # Step 6: Fraud check
    ok, flags, checks = check_fraud_indicators(claim_data, claim_history)
    all_fraud_flags.extend(flags)
    all_checks.extend(checks)

    # Network discount
    hospital = claim_data.get("hospital_name", "")
    network_discount, is_network = check_network_discount(hospital, claim_amount, policy)
    cashless = claim_data.get("cashless_request", False) and is_network

    if is_network and limits_ok:
        approved_amount = round(approved_amount - network_discount, 2) if approved_amount > 0 else 0
        deductions["network_discount"] = network_discount

    # Determine final decision
    unique_reasons = list(set(all_reasons))
    if all_fraud_flags:
        decision = "MANUAL_REVIEW"
        confidence = 0.65
    elif unique_reasons:
        if all_rejected_items and len(all_rejected_items) < len(treatments + medicines):
            decision = "PARTIAL"
            confidence = 0.88
        else:
            decision = "REJECTED"
            approved_amount = 0
            confidence = 0.95
    else:
        decision = "APPROVED"
        confidence = 0.92

    return {
        "decision": decision,
        "approved_amount": max(approved_amount, 0),
        "rejected_amount": claim_amount - max(approved_amount, 0),
        "rejection_reasons": unique_reasons,
        "rejected_items": all_rejected_items,
        "deductions": deductions,
        "confidence_score": confidence,
        "reasoning": generate_reasoning(decision, unique_reasons, all_checks),
        "notes": "",
        "next_steps": generate_next_steps(decision, unique_reasons),
        "fraud_flags": all_fraud_flags,
        "cashless_approved": cashless,
        "network_discount": network_discount if is_network else 0,
        "rule_checks": all_checks,
    }


def determine_category(extraction_results: List[dict]) -> str:
    """Determine the primary category of the claim from extracted data."""
    for doc in extraction_results:
        doc_type = doc.get("document_type", "other")
        if doc_type == "pharmacy_bill":
            return "pharmacy"
        diagnosis = (doc.get("diagnosis") or "").lower()
        if any(kw in diagnosis for kw in ["tooth", "dental", "root canal", "gum"]):
            return "dental"
        if any(kw in diagnosis for kw in ["eye", "vision", "myopia", "cataract"]):
            return "vision"
        if any(kw in diagnosis for kw in ["ayurveda", "homeopathy", "unani", "panchakarma"]):
            return "alternative_medicine"
        procedures = doc.get("procedures") or doc.get("tests_prescribed") or []
        for proc in procedures:
            if isinstance(proc, str) and any(kw in proc.lower() for kw in ["mri", "ct scan", "x-ray", "blood test", "ecg", "ultrasound"]):
                return "diagnostic"
    return "consultation"


def generate_reasoning(decision: str, reasons: List[str], checks: List[dict]) -> str:
    """Generate human-readable reasoning for the decision."""
    parts = [f"Decision: {decision}"]
    for check in checks:
        status = "✅" if check["status"] == "PASS" else "❌"
        parts.append(f"{status} {check['rule']}: {check['detail']}")
    return "\n".join(parts)


def generate_next_steps(decision: str, reasons: List[str]) -> str:
    """Generate actionable next steps for the claimant."""
    if decision == "APPROVED":
        return "Your claim has been approved. The reimbursement will be processed within 5-7 business days."
    elif decision == "PARTIAL":
        return "Some items in your claim were not covered. You may appeal for the rejected items within 15 days."
    elif decision == "MANUAL_REVIEW":
        return "Your claim has been flagged for manual review. A claims officer will review it within 2-3 business days."
    else:
        steps = ["Your claim has been rejected."]
        if "MISSING_DOCUMENTS" in reasons:
            steps.append("Please resubmit with all required documents (prescription, bills).")
        if "WAITING_PERIOD" in reasons:
            steps.append("This condition has a waiting period. Please check your eligibility date.")
        if "PER_CLAIM_EXCEEDED" in reasons:
            steps.append("The claim amount exceeds the per-claim limit. Consider splitting into multiple claims or contacting support.")
        if "PRE_AUTH_MISSING" in reasons:
            steps.append("Pre-authorization is required for this procedure. Please obtain approval before treatment.")
        steps.append("You may appeal this decision within 15 days.")
        return " ".join(steps)
