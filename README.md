# Provably Fair Trust Engine - FastAPI & Docker Backend

A production-ready, highly secure cryptographic Random Number Generator (RNG) and immutable audit ledger API built with FastAPI, Python, and SQLite. Perfect for gaming platforms, lotteries, and decentralized applications needing verifiable fairness.

## Features
- **SHA-256 Seed Pre-commitment:** Generates hidden server seeds and cryptographic hashes before gameplay.
- **Deterministic Outcome Calculation:** Combines server seeds, client seeds, and nonces to compute tamper-proof outcomes.
- **Immutable SQLite Ledger:** Automatically logs every verified round to a persistent audit trail.
- **Dockerized Architecture:** Zero-hassle deployment with Docker and Docker Compose.
- **Interactive Documentation:** Out-of-the-box Swagger UI and Redoc endpoints.

---

## Prerequisites
Ensure you have the following installed on your server:
- Docker Engine
- Docker Compose (v2+)

---

## Installation & Quick Start

1. **Clone or upload the project files** to your target server directory.
2. **Create a `.env` file** in the root directory (you can leave it blank or add custom configurations).
3. **Build and launch the container** using Docker Compose:
   ```bash
   docker compose up --build -d
