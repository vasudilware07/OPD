"""
Policy Router — API endpoints for viewing and configuring policy terms.
"""
import json
import os
from fastapi import APIRouter, HTTPException
from app.database import get_db

router = APIRouter(prefix="/api/policy", tags=["Policy"])

POLICY_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "..", "policy_terms.json")


@router.get("")
async def get_policy():
    """Get current policy terms."""
    db = get_db()
    # Try database first, fallback to file
    policy = await db.policy.find_one({"policy_id": "PLUM_OPD_2024"}, {"_id": 0})
    if not policy:
        with open(POLICY_FILE, "r") as f:
            policy = json.load(f)
    return policy


@router.put("")
async def update_policy(updates: dict):
    """Update policy configuration (admin endpoint)."""
    db = get_db()

    # Load current policy
    policy = await db.policy.find_one({"policy_id": "PLUM_OPD_2024"})
    if not policy:
        with open(POLICY_FILE, "r") as f:
            policy = json.load(f)
        await db.policy.insert_one(policy)

    # Apply updates
    for key, value in updates.items():
        if key not in ["_id", "policy_id"]:
            policy[key] = value

    await db.policy.update_one(
        {"policy_id": "PLUM_OPD_2024"},
        {"$set": updates}
    )

    # Also update the file
    policy.pop("_id", None)
    with open(POLICY_FILE, "w") as f:
        json.dump(policy, f, indent=2)

    return {"success": True, "message": "Policy updated", "policy": policy}


@router.get("/exclusions")
async def get_exclusions():
    """Get list of excluded treatments/conditions."""
    db = get_db()
    policy = await db.policy.find_one({"policy_id": "PLUM_OPD_2024"}, {"_id": 0})
    if not policy:
        with open(POLICY_FILE, "r") as f:
            policy = json.load(f)
    return {"exclusions": policy.get("exclusions", [])}


@router.get("/limits")
async def get_limits():
    """Get coverage limits breakdown."""
    db = get_db()
    policy = await db.policy.find_one({"policy_id": "PLUM_OPD_2024"}, {"_id": 0})
    if not policy:
        with open(POLICY_FILE, "r") as f:
            policy = json.load(f)
    return {
        "coverage_details": policy.get("coverage_details", {}),
        "waiting_periods": policy.get("waiting_periods", {}),
        "claim_requirements": policy.get("claim_requirements", {})
    }
