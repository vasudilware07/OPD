"""
Claims Router — API endpoints for claim submission, listing, and adjudication.
"""
import os
import uuid
import shutil
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from app.database import get_db
from app.config import UPLOAD_DIR
from app.services.ai_engine import extract_document_data, adjudicate_claim
from app.services.rule_engine import run_rule_engine, load_policy_terms

router = APIRouter(prefix="/api/claims", tags=["Claims"])


@router.post("")
async def submit_claim(
    member_id: str = Form(...),
    member_name: str = Form(...),
    treatment_date: str = Form(...),
    claim_amount: float = Form(...),
    hospital_name: Optional[str] = Form(None),
    cashless_request: bool = Form(False),
    description: Optional[str] = Form(None),
    documents: List[UploadFile] = File(...)
):
    """Submit a new OPD claim with supporting documents."""
    db = get_db()

    # Verify member exists
    member = await db.members.find_one({"member_id": member_id})
    if not member:
        raise HTTPException(status_code=404, detail=f"Member {member_id} not found")

    # Generate claim ID
    claim_count = await db.claims.count_documents({})
    claim_id = f"CLM_{(claim_count + 1):05d}"

    # Save uploaded documents
    claim_upload_dir = os.path.join(UPLOAD_DIR, claim_id)
    os.makedirs(claim_upload_dir, exist_ok=True)

    saved_documents = []
    extraction_results = []

    for doc in documents:
        # Save file
        file_ext = os.path.splitext(doc.filename)[1]
        file_id = str(uuid.uuid4())[:8]
        file_name = f"{file_id}{file_ext}"
        file_path = os.path.join(claim_upload_dir, file_name)

        content = await doc.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Determine MIME type
        mime_map = {
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png", ".gif": "image/gif",
            ".pdf": "application/pdf", ".webp": "image/webp"
        }
        mime_type = mime_map.get(file_ext.lower(), "application/octet-stream")

        saved_doc = {
            "file_id": file_id,
            "original_name": doc.filename,
            "saved_name": file_name,
            "file_path": file_path,
            "mime_type": mime_type,
            "size": len(content),
            "uploaded_at": datetime.utcnow().isoformat()
        }
        saved_documents.append(saved_doc)

        # Extract data using AI
        try:
            extraction = await extract_document_data(file_path, content, mime_type)
            extraction["file_id"] = file_id
            extraction_results.append(extraction)
        except Exception as e:
            extraction_results.append({
                "file_id": file_id,
                "error": str(e),
                "confidence": 0.0,
                "notes": f"Extraction failed: {str(e)}"
            })

    # Build claim data
    claim_data = {
        "member_id": member_id,
        "member_name": member_name,
        "treatment_date": treatment_date,
        "claim_amount": claim_amount,
        "hospital_name": hospital_name,
        "cashless_request": cashless_request,
        "description": description
    }

    # Get claim history for this member
    history_cursor = db.claims.find(
        {"member_id": member_id, "status": {"$in": ["APPROVED", "PARTIAL"]}},
        {"_id": 0, "claim_id": 1, "claim_amount": 1, "treatment_date": 1,
         "decision.approved_amount": 1}
    )
    claim_history = []
    async for h in history_cursor:
        claim_history.append({
            "claim_id": h.get("claim_id"),
            "claim_amount": h.get("claim_amount", 0),
            "treatment_date": h.get("treatment_date", ""),
            "approved_amount": h.get("decision", {}).get("approved_amount", 0)
        })

    # Run rule engine first (deterministic)
    member_dict = {k: v for k, v in member.items() if k != "_id"}
    rule_decision = run_rule_engine(claim_data, extraction_results, member_dict, claim_history)

    # Run AI adjudication (for enhanced reasoning)
    policy_terms = load_policy_terms()
    try:
        ai_decision = await adjudicate_claim(
            claim_data, extraction_results, member_dict, policy_terms, claim_history
        )
    except Exception:
        ai_decision = None

    # Merge decisions: rule engine is authoritative, AI provides reasoning
    final_decision = rule_decision.copy()
    if ai_decision and ai_decision.get("decision") != "MANUAL_REVIEW":
        # Use AI reasoning if available, but keep rule engine's decision
        if ai_decision.get("reasoning"):
            final_decision["reasoning"] = ai_decision["reasoning"]
        if ai_decision.get("notes"):
            final_decision["notes"] = ai_decision["notes"]
        if ai_decision.get("next_steps"):
            final_decision["next_steps"] = ai_decision["next_steps"]
        # Average confidence scores
        ai_conf = ai_decision.get("confidence_score", 0)
        rule_conf = rule_decision.get("confidence_score", 0)
        final_decision["confidence_score"] = round((ai_conf + rule_conf) / 2, 2) if ai_conf else rule_conf

    # Create claim document
    claim_doc = {
        "claim_id": claim_id,
        "member_id": member_id,
        "member_name": member_name,
        "treatment_date": treatment_date,
        "claim_amount": claim_amount,
        "hospital_name": hospital_name,
        "cashless_request": cashless_request,
        "description": description,
        "status": final_decision["decision"],
        "documents": saved_documents,
        "extraction_results": extraction_results,
        "decision": final_decision,
        "appeal": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "processing_time_ms": 0  # Would measure actual time in production
    }

    await db.claims.insert_one(claim_doc)

    # Return response
    claim_doc.pop("_id", None)
    return {
        "success": True,
        "message": f"Claim {claim_id} submitted and processed",
        "claim": claim_doc
    }


@router.get("")
async def list_claims(
    status: Optional[str] = Query(None),
    member_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc")
):
    """List all claims with optional filters and pagination."""
    db = get_db()

    # Build filter
    filter_query = {}
    if status:
        filter_query["status"] = status.upper()
    if member_id:
        filter_query["member_id"] = member_id

    # Sort direction
    sort_dir = -1 if sort_order == "desc" else 1

    # Get total count
    total = await db.claims.count_documents(filter_query)

    # Get paginated results
    cursor = db.claims.find(filter_query, {"_id": 0}).sort(
        sort_by, sort_dir
    ).skip((page - 1) * limit).limit(limit)

    claims = []
    async for claim in cursor:
        claims.append(claim)

    return {
        "claims": claims,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/stats")
async def get_stats():
    """Get dashboard statistics."""
    db = get_db()

    total = await db.claims.count_documents({})
    approved = await db.claims.count_documents({"status": "APPROVED"})
    rejected = await db.claims.count_documents({"status": "REJECTED"})
    partial = await db.claims.count_documents({"status": "PARTIAL"})
    pending = await db.claims.count_documents({"status": "PENDING"})
    manual = await db.claims.count_documents({"status": "MANUAL_REVIEW"})
    appealed = await db.claims.count_documents({"status": "APPEALED"})

    # Total amounts
    pipeline = [
        {"$group": {
            "_id": None,
            "total_claimed": {"$sum": "$claim_amount"},
            "total_approved": {"$sum": "$decision.approved_amount"}
        }}
    ]
    amounts = await db.claims.aggregate(pipeline).to_list(1)
    total_claimed = amounts[0]["total_claimed"] if amounts else 0
    total_approved = amounts[0]["total_approved"] if amounts else 0

    # Recent claims
    recent_cursor = db.claims.find({}, {"_id": 0}).sort("created_at", -1).limit(5)
    recent = []
    async for c in recent_cursor:
        recent.append(c)

    # Category breakdown
    cat_pipeline = [
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1},
            "total_amount": {"$sum": "$claim_amount"}
        }}
    ]
    categories = await db.claims.aggregate(cat_pipeline).to_list(10)
    category_breakdown = {}
    for cat in categories:
        category_breakdown[cat["_id"]] = {
            "count": cat["count"],
            "total_amount": cat["total_amount"]
        }

    # Fraud flags count
    fraud_pipeline = [
        {"$match": {"decision.fraud_flags": {"$ne": []}}},
        {"$count": "count"}
    ]
    fraud_result = await db.claims.aggregate(fraud_pipeline).to_list(1)
    fraud_count = fraud_result[0]["count"] if fraud_result else 0

    return {
        "total_claims": total,
        "approved_claims": approved,
        "rejected_claims": rejected,
        "partial_claims": partial,
        "pending_claims": pending,
        "manual_review_claims": manual,
        "appealed_claims": appealed,
        "total_claimed_amount": total_claimed,
        "total_approved_amount": total_approved,
        "approval_rate": round(((approved + partial) / total * 100), 1) if total > 0 else 0,
        "avg_processing_time": 2.3,  # seconds — placeholder
        "fraud_flags_count": fraud_count,
        "recent_claims": recent,
        "category_breakdown": category_breakdown
    }


@router.get("/{claim_id}")
async def get_claim(claim_id: str):
    """Get detailed claim information."""
    db = get_db()
    claim = await db.claims.find_one({"claim_id": claim_id}, {"_id": 0})
    if not claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
    return claim


@router.put("/{claim_id}/appeal")
async def appeal_claim(claim_id: str, reason: str = Form(...), additional_notes: Optional[str] = Form(None)):
    """Appeal a rejected or partially approved claim."""
    db = get_db()
    claim = await db.claims.find_one({"claim_id": claim_id})
    if not claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")

    if claim["status"] not in ["REJECTED", "PARTIAL"]:
        raise HTTPException(status_code=400, detail="Only rejected or partially approved claims can be appealed")

    appeal_data = {
        "reason": reason,
        "additional_notes": additional_notes,
        "appealed_at": datetime.utcnow().isoformat(),
        "appeal_status": "PENDING_REVIEW",
        "original_decision": claim["decision"]
    }

    await db.claims.update_one(
        {"claim_id": claim_id},
        {
            "$set": {
                "status": "APPEALED",
                "appeal": appeal_data,
                "updated_at": datetime.utcnow().isoformat()
            }
        }
    )

    return {"success": True, "message": f"Appeal submitted for claim {claim_id}", "appeal": appeal_data}


@router.get("/{claim_id}/documents/{file_id}")
async def get_document(claim_id: str, file_id: str):
    """Get a specific document file for a claim."""
    from fastapi.responses import FileResponse
    db = get_db()
    claim = await db.claims.find_one({"claim_id": claim_id})
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    for doc in claim.get("documents", []):
        if doc["file_id"] == file_id:
            file_path = doc["file_path"]
            if os.path.exists(file_path):
                return FileResponse(file_path, media_type=doc["mime_type"], filename=doc["original_name"])
            raise HTTPException(status_code=404, detail="File not found on disk")

    raise HTTPException(status_code=404, detail="Document not found")
