# QAInspect Pro

**QAInspect Pro** is a comprehensive Software Quality Assurance (SQA) platform designed to automate frontend, backend, security, and performance testing while providing advanced test case management and professional reporting dashboards.

## Project Structure

This repository is split into two core workspaces:

- `frontend/`: React + Vite + TailwindCSS application for the Test Management Dashboard.
- `backend/`: FastAPI + PostgreSQL backend for Test Execution API and database modelling.

## Running the Application

### 1. Backend Setup

The backend requires Python 3.9+.
It can run with the default SQLite database or be configured to use PostgreSQL via `DATABASE_URL` in `.env`.

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # (Windows)
pip install -r requirements.txt
cp ../.env.example .env
# Update .env with your specific settings before starting.
uvicorn main:app --reload
```

#### Run backend tests

```bash
cd ..
pytest backend/tests
```

### 2. Frontend Setup

The frontend runs on NodeJS 18+.

```bash
cd frontend
npm install
npm run dev
```

## Features & Intelligence Engine

- **Automated Intelligence Engine**: Real-time analysis of target URLs for Security and Performance metrics.
- **Advanced Security Audit**: 
  - SSL/TLS certificate validation (expiry and issuer details).
  - Critical security header checks (HSTS, CSP, X-Frame-Options, etc.).
  - Information disclosure prevention checks.
- **Performance Matrix**:
  - Response time and TTLB (Time to Last Byte) analysis.
  - Payload size tracking and efficiency scoring.
- **Smart Recommendations**: Dynamic AI-driven suggestions based on scan results (e.g., asset compression, header hardening).
- **Test Repository**: Automated seeding of 1000+ comprehensive SQA test cases (Functional, Performance, Security, Compatibility).
- **Executive Reporting**: Dynamic dashboards with historical execution streams and CSV exporting.
- **Modern User Experience**: High-performance Glassmorphic UI with real-time health gauges and animations.

## Project Structure

- `frontend/`: React + Vite + TailwindCSS application (Intelligence Dashboard).
- `backend/`: FastAPI + SQLAlchemy for Test Execution and automated quality mapping.
- `test_engine/`: Core Python scanners for network and web intelligence.
- `test_cases/`: Seed data engine for populating industry-standard test repositories.
