# Verifiable Delay Function VDF

Educational Wesolowski verifiable delay function demonstration, with independent legacy threshold-audit CLI and FastAPI services.

## Features

- **Browser demonstration:** sequential modular squaring with JavaScript BigInt, SHA-256-derived 64-bit prime challenge, quotient proof generation, transcript-bound verification, JSON export, and tampering tests. No Python runtime or server is required.
- **Python demonstration:** the same proof arithmetic in **vdf_engine/wesolowski.py**, exposed through the installed CLI.
- **Legacy audit workflows:** rule-based parameter threshold checks, CSV processing, supervisory queries, and two FastAPI audit server variants. These are not cryptographic VDFs.

**Cryptographic warning:** This is an educational implementation, **not a production-secure VDF**. The example modulus 1000036000099 = 1000003 × 1000033 has known factors. The proof challenge is only 64 bits; no secure unknown-order group ceremony or independent security audit is provided. Do not use it for blockchain consensus, randomness beacons, lotteries, or other security-sensitive applications. NIST FIPS 203/204/205 are not VDF certifications.

## Browser use

Open the static site under **web/** (or serve that directory locally), enter an odd modulus, coprime base, and 1–10,000 squarings, then select **Evaluate and prove**. Verification automatically follows. Edit the JSON transcript and select **Verify transcript** to test modified-proof rejection. Inputs and proof generation remain in your browser; there are no analytics or API calls.

GitHub Pages hosts only the browser version; it does not host the Python servers. Deployment is configured through **.github/workflows/pages.yml** but must be checked in GitHub Pages settings and verified before relying on the public URL.

## Python installation and tests

~~~bash
git clone https://github.com/abusuraihsakhri/verifiable-delay-function-vdf.git
cd verifiable-delay-function-vdf
python -m pip install -e '.[server,dev]'
python -m vdf_engine.cli vdf --modulus 1000036000099 --base 5 --iterations 512
python -m pytest -q
node --check web/vdf.js
node --test tests/test_browser_vdf.cjs
~~~

The Python proof represents integers as JSON numbers; the browser represents them as decimal strings to avoid JavaScript integer-precision loss.

## Legacy audit services

~~~bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
~~~

The primary FastAPI service **agents.api:app** exposes GET /health, GET /metrics, POST /api/audit, POST /api/chat, and GET /api/audit/logs. The separate **vdf_engine.server** exposes a smaller audit API. Neither provides VDF-proof endpoints.

For Docker Compose, set a unique secret at runtime (for example, generate one with Python's secrets.token_hex(32) and export **AUDIT_SECRET_KEY**) and run **docker compose up --build**. Never commit the actual key. Without a configured key the runtime generates an ephemeral key, so audit verification does not persist across restarts.

**Security and privacy:** the REST API has no authentication and must remain bound to localhost or be protected by an authenticated gateway. The identifier regex filter is heuristic, not a guarantee of de-identification or medical regulatory compliance. Audit logs and supervisor registries are held in process memory; no durable audit storage is implemented. HTTP API data are transmitted to the server, while browser VDF processing is local.

## Development and compatibility

Python >=3.10, Pydantic 2, optional FastAPI/Uvicorn, and pytest; JavaScript BigInt and Web Crypto in current Chromium, Firefox, or Safari. GitHub Actions runs Python tests, JavaScript algorithm checks, and compilation. No Pyodide or server-side Python is used on GitHub Pages.

MIT license. See [LICENSE](LICENSE).
