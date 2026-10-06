# SaaS Access Governance Agent (Okta Identity Auditor)

An automated Identity and Access Management (IAM) security agent that ingests enterprise Okta System Logs, processes authentication metadata, and utilizes Gemini AI orchestration to identify anomalous behavior, impossible travel metrics, privilege creep, and malicious MFA lifecycle manipulations.

## Business & Operational Impact
* **Reduces MTTR (Mean Time to Resolution):** Instantly parses raw JSON payload data into readable, structured Markdown incident reports for security operations.
* **Hardens IAM Compliance:** Automated runtime monitoring flags drift from Least Privilege access controls.
* **Optimizes SOC Efficiency:** Offloads initial threat categorization workflows to a localized LLM agent.

## Technical Architecture
The engine reads native Okta event logs (`user.session.start`, `user.mfa.factor.deactivate`, `user.account.privilege.grant`). If suspicious access loops occur (e.g., an implicit MFA deactivation immediately followed by a Super Admin promotion via a non-standard IP subnet), the pipeline triggers the `gemini-1.5-flash` operational context layer to draft an automated incident report and remediation runbook.

## Step-by-Step Execution Guide

1. Clone the operational repository:
   ```bash
   git clone https://github.com/HexieB/saas-access-governance-agent.git
   cd saas-access-governance-agent
   ```

2. Establish your dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Export your enterprise Gemini API credential:
   ```bash
   export GOOGLE_API_KEY="your-api-key-here"
   ```

4. Execute the runtime governance audit:
   ```bash
   python audit_agent.py
   ```
