"""
Database seeder — Populates MongoDB with sample members, policy terms, and demo claims.
"""
import asyncio
import json
import os
import sys

# Add parent to path
sys.path.insert(0, os.path.dirname(__file__))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "plum_opd")


# ─── Sample Members ──────────────────────────────────────────────────────────

SAMPLE_MEMBERS = [
    {
        "member_id": "EMP001",
        "name": "Rajesh Kumar",
        "email": "rajesh.kumar@techcorp.com",
        "age": 35,
        "gender": "Male",
        "join_date": "2024-01-15",
        "policy_status": "active",
        "department": "Engineering",
        "designation": "Senior Software Engineer",
        "dependents": [
            {"name": "Priya Kumar", "relation": "Spouse", "age": 32},
            {"name": "Arjun Kumar", "relation": "Child", "age": 8}
        ]
    },
    {
        "member_id": "EMP002",
        "name": "Priya Singh",
        "email": "priya.singh@techcorp.com",
        "age": 28,
        "gender": "Female",
        "join_date": "2024-02-01",
        "policy_status": "active",
        "department": "Product",
        "designation": "Product Manager",
        "dependents": []
    },
    {
        "member_id": "EMP003",
        "name": "Amit Verma",
        "email": "amit.verma@techcorp.com",
        "age": 42,
        "gender": "Male",
        "join_date": "2024-01-01",
        "policy_status": "active",
        "department": "Finance",
        "designation": "Finance Manager",
        "dependents": [
            {"name": "Sunita Verma", "relation": "Spouse", "age": 39},
            {"name": "Rahul Verma", "relation": "Child", "age": 14},
            {"name": "Neha Verma", "relation": "Child", "age": 10}
        ]
    },
    {
        "member_id": "EMP004",
        "name": "Sneha Reddy",
        "email": "sneha.reddy@techcorp.com",
        "age": 31,
        "gender": "Female",
        "join_date": "2024-03-15",
        "policy_status": "active",
        "department": "Marketing",
        "designation": "Marketing Lead",
        "dependents": []
    },
    {
        "member_id": "EMP005",
        "name": "Vikram Joshi",
        "email": "vikram.joshi@techcorp.com",
        "age": 45,
        "gender": "Male",
        "join_date": "2024-09-01",
        "policy_status": "active",
        "department": "Operations",
        "designation": "Operations Head",
        "dependents": [
            {"name": "Meera Joshi", "relation": "Spouse", "age": 42}
        ]
    },
    {
        "member_id": "EMP006",
        "name": "Kavita Nair",
        "email": "kavita.nair@techcorp.com",
        "age": 38,
        "gender": "Female",
        "join_date": "2024-02-15",
        "policy_status": "active",
        "department": "HR",
        "designation": "HR Manager",
        "dependents": [
            {"name": "Anand Nair", "relation": "Spouse", "age": 40}
        ]
    },
    {
        "member_id": "EMP007",
        "name": "Suresh Patil",
        "email": "suresh.patil@techcorp.com",
        "age": 50,
        "gender": "Male",
        "join_date": "2024-01-01",
        "policy_status": "active",
        "department": "Engineering",
        "designation": "VP Engineering",
        "dependents": [
            {"name": "Lakshmi Patil", "relation": "Spouse", "age": 47},
            {"name": "Aditya Patil", "relation": "Child", "age": 22}
        ]
    },
    {
        "member_id": "EMP008",
        "name": "Ravi Menon",
        "email": "ravi.menon@techcorp.com",
        "age": 33,
        "gender": "Male",
        "join_date": "2024-04-01",
        "policy_status": "active",
        "department": "Sales",
        "designation": "Sales Manager",
        "dependents": []
    },
    {
        "member_id": "EMP009",
        "name": "Anita Desai",
        "email": "anita.desai@techcorp.com",
        "age": 29,
        "gender": "Female",
        "join_date": "2024-05-01",
        "policy_status": "active",
        "department": "Design",
        "designation": "UI/UX Designer",
        "dependents": []
    },
    {
        "member_id": "EMP010",
        "name": "Deepak Shah",
        "email": "deepak.shah@techcorp.com",
        "age": 36,
        "gender": "Male",
        "join_date": "2024-01-01",
        "policy_status": "active",
        "department": "Engineering",
        "designation": "Tech Lead",
        "dependents": [
            {"name": "Nisha Shah", "relation": "Spouse", "age": 34},
            {"name": "Kavya Shah", "relation": "Child", "age": 5}
        ]
    }
]


async def seed_database():
    """Seed the MongoDB database with sample data."""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    print("[SEED] Seeding database...")

    # Clear existing data
    await db.members.drop()
    await db.claims.drop()
    await db.policy.drop()
    print("  [OK] Cleared existing collections")

    # Seed members
    await db.members.insert_many(SAMPLE_MEMBERS)
    print(f"  [OK] Inserted {len(SAMPLE_MEMBERS)} members")

    # Create indexes
    await db.members.create_index("member_id", unique=True)
    await db.claims.create_index("claim_id", unique=True)
    await db.claims.create_index("member_id")
    await db.claims.create_index("status")
    await db.claims.create_index("created_at")

    # Seed policy
    policy_path = os.path.join(os.path.dirname(__file__), "..", "policy_terms.json")
    with open(policy_path, "r") as f:
        policy = json.load(f)
    await db.policy.insert_one(policy)
    print("  [OK] Inserted policy terms")

    print("[DONE] Database seeded successfully!")
    print(f"   Database: {DATABASE_NAME}")
    print(f"   Members: {len(SAMPLE_MEMBERS)}")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
