"""
Members Router — API endpoints for member management.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.database import get_db

router = APIRouter(prefix="/api/members", tags=["Members"])


@router.get("")
async def list_members(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    """List all policy members with optional search."""
    db = get_db()

    filter_query = {}
    if search:
        filter_query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"member_id": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]

    total = await db.members.count_documents(filter_query)
    cursor = db.members.find(filter_query, {"_id": 0}).skip((page - 1) * limit).limit(limit)

    members = []
    async for member in cursor:
        # Get claims summary for each member
        claims_count = await db.claims.count_documents({"member_id": member["member_id"]})
        approved_count = await db.claims.count_documents(
            {"member_id": member["member_id"], "status": {"$in": ["APPROVED", "PARTIAL"]}}
        )

        # Calculate total approved amount
        pipeline = [
            {"$match": {"member_id": member["member_id"], "status": {"$in": ["APPROVED", "PARTIAL"]}}},
            {"$group": {"_id": None, "total": {"$sum": "$decision.approved_amount"}}}
        ]
        result = await db.claims.aggregate(pipeline).to_list(1)
        total_approved = result[0]["total"] if result else 0

        member["claims_summary"] = {
            "total_claims": claims_count,
            "approved_claims": approved_count,
            "total_approved_amount": total_approved,
            "remaining_annual_limit": 50000 - total_approved
        }
        members.append(member)

    return {
        "members": members,
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/{member_id}")
async def get_member(member_id: str):
    """Get detailed member information with claim history."""
    db = get_db()
    member = await db.members.find_one({"member_id": member_id}, {"_id": 0})
    if not member:
        raise HTTPException(status_code=404, detail=f"Member {member_id} not found")

    # Get all claims for this member
    cursor = db.claims.find(
        {"member_id": member_id},
        {"_id": 0}
    ).sort("created_at", -1)

    claims = []
    async for claim in cursor:
        claims.append(claim)

    # Calculate summary
    total_claimed = sum(c.get("claim_amount", 0) for c in claims)
    total_approved = sum(c.get("decision", {}).get("approved_amount", 0) for c in claims)

    member["claims"] = claims
    member["claims_summary"] = {
        "total_claims": len(claims),
        "approved_claims": sum(1 for c in claims if c.get("status") in ["APPROVED", "PARTIAL"]),
        "rejected_claims": sum(1 for c in claims if c.get("status") == "REJECTED"),
        "total_claimed_amount": total_claimed,
        "total_approved_amount": total_approved,
        "remaining_annual_limit": 50000 - total_approved
    }

    return member
