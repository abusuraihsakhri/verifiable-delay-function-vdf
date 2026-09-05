# Verifiable Delay Function VDF

> **Domain:** Post-Quantum Cryptography & Zero-Knowledge Architecture
> **Reference Guidelines & Standards:** NIST FIPS 203/204/205, NIST SP 800-90B & ISO/IEC Standards

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Tests](https://img.shields.io/badge/Tests-35_Passed-brightgreen.svg)

</div>

---

## Overview

**Verifiable Delay Function VDF** implements Pietrzak / Wesolowski Verifiable Delay Function (VDF) evaluation with a multi-agent consensus architecture. The system provides sequential squaring evaluation, safety boundary enforcement, and protocol conformance checking with tamper-evident audit logging.

---

## Architecture

The project consists of two parallel evaluation engines:

### 1. Agents System (`agents/`)
- **Multi-worker consensus**: InvariantQC, SafetyEscalation, and ProtocolConformance workers
- **PHI outbound guard**: Prevents sensitive data leakage via regex pattern detection
- **HMAC-SHA256 audit trail**: Cryptographically chained, tamper-evident logging
- **FastAPI REST server**: OpenAPI endpoints for audit, chat, and metrics

### 2. VDF Engine (`vdf_engine/`)
- **Sequential Squaring Worker**: Primary parameter boundary auditor
- **Wesolowski Proof Prover**: Critical kinetics and security safeguard
- **Submillisecond Verifier**: Protocol conformance and anomaly triage
- **VDF Coordinator**: Executive coordinator with execution ledger

### 3. Enrichment Suite (`enrichment.py`)
- Performance Benchmarking with operation counts and timing
- Side-Channel Resistance Analysis (constant-time verification)
- Interoperability Testing against liboqs, pqcrypto, BoringSSL vectors
- VDF Scalability Analysis (sequential time vs proof size)
- Formal Security Proof Documentation
- NIST Compliance Certification Checklist
- Blockchain VDF Simulator
- Parallel Verification Optimizer

---

## Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/verifiable-delay-function-vdf.git
cd verifiable-delay-function-vdf

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

---

## Usage

### CLI Commands

#### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

#### 2. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

#### 3. Supervisory Chat
```bash
python cli.py chat "What is the system status?"
```

#### 4. Verify Audit Integrity
```bash
python cli.py verify-audit
```

#### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### VDF Engine CLI
```bash
python vdf_engine/cli.py audit --task-id TASK-001 --primary 29.4 --secondary 15.1 --critical --status DISCORDANT
python vdf_engine/cli.py chat "What standard is applied?"
```

### REST API Endpoints

| Endpoint | Method | Description |
|:---------|:-------|:------------|
| `/health` | GET | Service health check |
| `/metrics` | GET | Operational metrics |
| `/api/audit` | POST | Submit task for evaluation |
| `/api/chat` | POST | Query supervisory intelligence |
| `/api/audit/logs` | GET | Retrieve audit trail with integrity verification |

### Simulation
```bash
python simulator.py 100
```

---

## Security Features

- **Zero-PHI Outbound Interceptor**: AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers
- **Tamper-Evident HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs with signature verification
- **Input Validation**: Bounds checking, path traversal prevention, and injection character filtering
- **Secure Key Generation**: Cryptographically random audit key generation (falls back to `AUDIT_SECRET_KEY` env var)

---

## Testing

```bash
# Run full test suite (35 tests)
pytest -v

# Run specific test modules
pytest tests/test_security_and_validation.py -v
pytest tests/test_enrichment.py -v
pytest tests/test_vdf_engine.py -v
```

---

## Docker Deployment

```bash
docker build -t verifiable-delay-function-vdf .
docker run -p 8000:8000 verifiable-delay-function-vdf
```

---

## Project Structure

```
verifiable-delay-function-vdf/
├── agents/                  # Multi-agent consensus system
│   ├── api.py              # FastAPI REST server
│   ├── base.py             # Security, PHI guard, audit trail
│   ├── models.py           # Pydantic data models
│   ├── supervisor.py       # Orchestrator
│   ├── workers.py          # Specialized evaluation workers
│   ├── llm_factory.py      # LLM provider abstraction
│   ├── learning.py         # Bayesian calibration engine
│   ├── metrics.py          # Prometheus metrics
│   └── streamer.py         # WebSocket telemetry
├── vdf_engine/             # Core VDF evaluation engine
│   ├── engine.py           # Core algorithmic engine
│   ├── agents.py           # VDF worker agents
│   ├── models.py           # Data models
│   ├── cli.py              # CLI interface
│   └── server.py           # FastAPI server factory
├── tests/                  # Test suite
├── cli.py                  # Main CLI entry point
├── simulator.py            # High-throughput simulation
├── enrichment.py           # Enrichment feature suite
├── pyproject.toml          # Project configuration
├── Dockerfile              # Container definition
└── docker-compose.yml      # Compose configuration
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
