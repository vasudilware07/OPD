"""Pydantic models for API request/response schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ClaimStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PARTIAL = "PARTIAL"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    APPEALED = "APPEALED"


class DocumentType(str, Enum):
    PRESCRIPTION = "prescription"
    BILL = "bill"
    DIAGNOSTIC_REPORT = "diagnostic_report"
    PHARMACY_BILL = "pharmacy_bill"
    OTHER = "other"


# ─── Request Models ───────────────────────────────────────────────────────────

class ClaimSubmission(BaseModel):
    member_id: str
    member_name: str
    treatment_date: str
    claim_amount: float
    hospital_name: Optional[str] = None
    cashless_request: bool = False
    description: Optional[str] = None


class AppealRequest(BaseModel):
    reason: str
    additional_notes: Optional[str] = None


class PolicyUpdate(BaseModel):
    coverage_details: Optional[dict] = None
    exclusions: Optional[List[str]] = None
    waiting_periods: Optional[dict] = None


# ─── Response Models ──────────────────────────────────────────────────────────

class ExtractionResult(BaseModel):
    patient_name: Optional[str] = None
    patient_age: Optional[str] = None
    patient_gender: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_registration: Optional[str] = None
    doctor_qualification: Optional[str] = None
    clinic_name: Optional[str] = None
    clinic_address: Optional[str] = None
    treatment_date: Optional[str] = None
    diagnosis: Optional[str] = None
    chief_complaints: Optional[List[str]] = None
    medicines_prescribed: Optional[List[dict]] = None
    tests_prescribed: Optional[List[str]] = None
    procedures: Optional[List[str]] = None
    bill_items: Optional[List[dict]] = None
    total_amount: Optional[float] = None
    payment_mode: Optional[str] = None
    document_type: Optional[str] = None
    confidence: float = 0.0
    raw_text: Optional[str] = None
    notes: Optional[str] = None


class AdjudicationDecision(BaseModel):
    claim_id: str
    decision: ClaimStatus
    approved_amount: float = 0
    rejected_amount: float = 0
    rejection_reasons: List[str] = []
    rejected_items: List[str] = []
    deductions: dict = {}
    confidence_score: float = 0.0
    reasoning: str = ""
    notes: str = ""
    next_steps: str = ""
    fraud_flags: List[str] = []
    cashless_approved: bool = False
    network_discount: float = 0
    rule_checks: List[dict] = []


class ClaimResponse(BaseModel):
    id: str
    claim_id: str
    member_id: str
    member_name: str
    treatment_date: str
    claim_amount: float
    status: ClaimStatus
    hospital_name: Optional[str] = None
    cashless_request: bool = False
    documents: List[dict] = []
    extraction_results: List[dict] = []
    decision: Optional[dict] = None
    appeal: Optional[dict] = None
    created_at: str
    updated_at: str


class MemberResponse(BaseModel):
    member_id: str
    name: str
    email: str
    age: int
    gender: str
    join_date: str
    policy_status: str
    department: Optional[str] = None
    dependents: List[dict] = []
    claims_summary: dict = {}


class DashboardStats(BaseModel):
    total_claims: int = 0
    approved_claims: int = 0
    rejected_claims: int = 0
    partial_claims: int = 0
    pending_claims: int = 0
    manual_review_claims: int = 0
    total_claimed_amount: float = 0
    total_approved_amount: float = 0
    approval_rate: float = 0
    avg_processing_time: float = 0
    fraud_flags_count: int = 0
    recent_claims: List[dict] = []
    category_breakdown: dict = {}
