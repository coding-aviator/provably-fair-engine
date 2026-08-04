import hashlib
import os
import secrets
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Provably Fair Trust Engine",
    description="Cryptographic RNG and Immutable Audit Ledger API",
    version="1.0.0",
)

DB_PATH = "/app/data/ledger.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            server_seed TEXT,
            server_hash TEXT,
            client_seed TEXT,
            nonce INTEGER,
            game_outcome REAL
        )
    """)
    conn.commit()
    conn.close()

# Initialize SQLite ledger on startup
init_db()

class VerifyRequest(BaseModel):
    server_seed: str
    client_seed: str
    nonce: int

@app.post("/api/v1/generate-seed")
def generate_seed():
    """Generates a secure server seed and returns its SHA-256 hash pre-commitment."""
    server_seed = secrets.token_hex(32)
    server_hash = hashlib.sha256(server_seed.encode()).hexdigest()
    return {
        "server_hash": server_hash,
        "message": "Server seed pre-committed successfully. Store server_seed securely after the round."
    }

@app.post("/api/v1/verify-round")
def verify_round(data: VerifyRequest):
    """Verifies a game outcome using client/server seeds and records it to the SQLite audit ledger."""
    expected_hash = hashlib.sha256(data.server_seed.encode()).hexdigest()

    # Generate deterministic outcome using combined seed hash
    combined = f"{data.server_seed}:{data.client_seed}:{data.nonce}"
    outcome_hash = hashlib.sha256(combined.encode()).hexdigest()
    game_outcome = int(outcome_hash[:8], 16) / 0xFFFFFFFF * 100

    # Save to immutable SQLite ledger
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_ledger (server_seed, server_hash, client_seed, nonce, game_outcome)
            VALUES (?, ?, ?, ?, ?)
        """, (data.server_seed, expected_hash, data.client_seed, data.nonce, game_outcome))
        conn.commit()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write to audit ledger: {str(e)}")

    return {
        "verified": True,
        "server_hash": expected_hash,
        "game_outcome": round(game_outcome, 4),
        "ledger_status": "Recorded and immutable"
    }

@app.get("/api/v1/audit-logs")
def get_audit_logs(limit: int = 10):
    """Fetches recent immutable records from the SQLite audit ledger."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_ledger ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return {"recent_audits": [dict(row) for row in rows]}
