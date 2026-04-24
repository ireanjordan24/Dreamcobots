# Security Auditor Bot

## Overview
Scans Python code and configuration files for security vulnerabilities using
`bandit`, the industry-standard Python security linter. Protects your
codebase and clients from data exposure and common attack vectors.

## What It Does
- Runs `bandit -r` on any file or directory
- Parses JSON output into structured severity buckets (HIGH / MEDIUM / LOW)
- Reports file paths, line numbers, test IDs, and descriptions
- Exits with code 1 when HIGH or MEDIUM severity issues are found

## Features
- Zero manual configuration required for standard Python projects
- Structured JSON report for downstream processing
- Integrates seamlessly with CI pipelines and the Task Execution Controller
- Distinguishes severity levels so teams can triage efficiently

## Benefits
- Prevents secrets from being committed (hardcoded passwords, API keys)
- Catches unsafe use of `eval`, `exec`, `subprocess` with shell=True, etc.
- Keeps client-facing systems compliant with basic security standards

## Example Use Case
```python
from bots.security_auditor_bot import run_bandit

report = run_bandit("bots/")
print(f"HIGH: {report['high_count']}  MEDIUM: {report['medium_count']}")
```

## Command Line
```bash
python bots/security_auditor_bot.py bots/
python bots/security_auditor_bot.py core/
```

## Future Enhancements
- OWASP top-10 mapping for each finding
- Auto-remediation for simple issues (e.g., replace `md5` with `sha256`)
- Integration with GitHub Security Advisories API
