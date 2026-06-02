# SQA Assignment: Role of SQA Engineer in SDLC & SRS Development

**Course Code:** CLO2: C3 Apply, GA3  
**Project Name:** QAInspect Pro  
**Submission Date:** April 2, 2026  

---

## Part 1: Project Overview

### Project Title
**QAInspect Pro - Enterprise Intelligence & Test Management Suite**

### Purpose of the System
QAInspect Pro is designed to bridge the gap between automated scanning and formal test management. It provides a centralized hub for SQA Engineers to perform security audits, performance benchmarking, and manage a massive repository of over 1,000 industry-standard test cases. The system aims to replace manual spreadsheets and fragmented tools with a unified, high-performance platform.

### Target Users
- **SQA Engineers:** To execute automated scans and manage test repositories.
- **Security Analysts:** To review SSL/TLS and security header status.
- **DevOps/SREs:** To monitor performance metrics like TTLB and payload efficiency.
- **Project Managers:** To view high-level executive reports and quality trends.

### Key Features
1.  **Automated Intelligence Engine:** Real-time URL analysis for security and network health.
2.  **Security Audit Pro:** Automated checks for HSTS, CSP, X-Frame-Options, and SSL expiry.
3.  **Performance Matrix:** Detailed breakdown of response times, payload sizes, and efficiency scores.
4.  **1000+ Industry-Standard Test Cases:** Pre-built functional, security, and performance test templates.
5.  **Executive Reporting Dashboard:** Dynamic glassmorphic UI with CSV export and historical tracking.

---

## Part 2: Role of SQA Engineer in SDLC

| SDLC Phase | SQA Engineer Activities | Artifacts/Deliverables Produced | Contribution to Quality | Preparation for Next Phase |
| :--- | :--- | :--- | :--- | :--- |
| **1. Requirement Analysis** | Reviewing SRS for clarity, completeness, and testability. Identifying potential risks. | Requirement Traceability Matrix (RTM), QA Strategy Document. | Ensures building the *right* system by preventing "garbage-in." | Identifying tools and resources needed for the system. |
| **2. Design Phase** | Reviewing system architecture and database design (e.g., SQLAlchemy mappings). | Test Plan, High-Level Test Design. | Detects architectural flaws (logic errors) before code is written. | Mapping test cases to specific design modules. |
| **3. Development** | White-box testing, Code reviews, and setting up Test Data (e.g., `seed_data.py`). | Unit Test Results, Static Analysis Reports. | Prevents bugs from entering the main codebase; verifies logic early. | Finalizing test scripts for integration and system testing. |
| **4. Testing Phase** | Execution of Functional, Security, and Performance tests on the build. | Bug Reports (Jira), Test Execution Reports. | Verifies the system meets requirements and is stable for production. | Creating a "Go/No-Go" readiness report for deployment. |
| **5. Deployment/Maint.** | Smoke testing on production and verifying fixes for reported field bugs. | Release Notes, Final Quality Sign-off. | Ensures zero regression and validates the system in the real user environment. | Updating regression suites for future cycles. |

---

## Part 3: Software Requirements Specification (SRS)

### 1. Introduction
#### 1.1 Purpose
The purpose of this document is to define the functional and non-functional requirements for **QAInspect Pro v1.0**. It provides a baseline for development and testing.

#### 1.2 Scope
QAInspect Pro is a web-based intelligence scanner and test management system. It integrates a FastAPI backend with a React frontend to provide real-time quality insights.

#### 1.3 Definitions
- **TTLB:** Time To Last Byte (Total response time).
- **HSTS:** HTTP Strict Transport Security.
- **Glassmorphism:** A design style characterized by background blur and translucent layers.

### 2. Overall Description
#### 2.1 Product Perspective
QAInspect Pro is a standalone intelligence suite that can be integrated into CI/CD pipelines via API. It utilizes a PostgreSQL database for historical data persistence.

#### 2.2 User Characteristics
Users are expected to have a basic understanding of web security (HTTPS/Headers) and SQA terminologies.

#### 2.3 Assumptions and Constraints
- **Assumptions:** Target URLs are publicly accessible via the Internet.
- **Constraints:** Scans are limited to HTTP/HTTPS protocols only.

### 3. Functional Requirements
- **FR1: Target Scanning:** The system shall allow users to input a URL and initiate a multi-threaded security and performance scan.
- **FR2: Security Validation:** The system shall check for the presence of mandatory security headers (CSP, HSTS, X-Content-Type).
- **FR3: Test Case Repository:** The system shall store and display 1,000+ pre-defined test cases categorized by functional domains.
- **FR4: Report Export:** Users shall be able to export scan results and test case statuses in CSV format.

### 4. Non-Functional Requirements
- **NFR1: Performance:** The intelligence engine must complete a basic URL scan (headers + latency) in under 5 seconds.
- **NFR2: UI/UX:** The dashboard must adhere to the **Glassmorphism design system** with a minimum 90% accessibility score (Lighthouse).
- **NFR3: Scalability:** The system shall support concurrent scanning of 5 different URLs without performance degradation.

---

## Part 4: Making Requirements Testable & Measurable

| Original (Raw) Requirement | Improved (Testable) Requirement | Measurable Criteria |
| :--- | :--- | :--- |
| "The system should be very fast when scanning." | "The backend scanner must return the complete header and latency analysis for a standard URL within a specific time frame." | **Response Time < 5.0 seconds** for 95% of scanned URLs on a 100Mbps connection. |
| "The dashboard should handle many test cases." | "The frontend must render a list of 1,000 test cases with smooth scrolling and filter responsiveness." | **Frame Rate >= 60 FPS** during scrolling; filtering must update in **< 200ms**. |
| "Users should be able to see security risks." | "The system shall flag any missing security headers (HSTS, CSP, XFO) as CRITICAL in the report." | **100% Accuracy** in header detection validated against OWASP ZAP benchmarks. |
| "The system should be easy to use." | "Users must be able to navigate from the home screen to a full scan report in no more than 3 clicks." | **Success rate of 98%** in usability testing for first-time SQA users. |

---
