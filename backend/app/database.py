"""MongoDB connection and database utilities using Motor (async driver)."""
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGODB_URL, DATABASE_NAME

client: AsyncIOMotorClient = None
db = None


async def connect_db():
    """Connect to MongoDB and initialize the database reference."""
    global client, db
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    # Create indexes for performance
    await db.claims.create_index("claim_id", unique=True)
    await db.claims.create_index("member_id")
    await db.claims.create_index("status")
    await db.claims.create_index("created_at")
    await db.members.create_index("member_id", unique=True)
    print(f"[OK] Connected to MongoDB: {DATABASE_NAME}")


async def close_db():
    """Close the MongoDB connection."""
    global client
    if client:
        client.close()
        print("[OK] MongoDB connection closed")


def get_db():
    """Get the database instance."""
    return db
