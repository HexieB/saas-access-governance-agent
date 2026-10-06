import os
import json
import argparse
import glob
from google import genai
from google.genai import errors

if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"):
    raise ValueError("CRITICAL: GEMINI_API_KEY or GOOGLE_API_KEY is missing from runtime context.")

client = genai.Client()

def parse_arguments():
    """Establishes robust CLI argument handling for files or full directories."""
    parser = argparse.ArgumentParser(description="Enterprise IAM Governance Agent - Batch Auditing Pipeline.")
    parser.add_argument(
        "--src",
        type=str,
        help="Path to a single Okta log JSON file OR a directory containing multiple JSON files.",
        default=None
    )
    return parser.parse_args()

def get_target_path(args):
    """Determines target path, prompting interactive input if executed bare."""
    if args.src:
        return args.src
    print("=== Identity Governance Agent Ingestion Pipeline ===")
    user_input = input("Enter file path or directory path (Leave blank for 'mock_okta_logs.json'): ").strip()
    return user_input if user_input else "mock_okta_logs.json"

def process_single_payload(file_path):
    """Validates and ingests a single target log file."""
    expanded_path = os.path.abspath(os.path.expanduser(file_path))
    if not os.path.exists(expanded_path):
        raise FileNotFoundError(f"Target file missing: {expanded_path}")
        
    with open(expanded_path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Data Corruption: {file_path} is not valid JSON.")

def execute_ai_governance_audit(log_payload, file_name):
    """Orchestrates Gemini 2.5 to evaluate the provided log payload."""
    prompt = f"""
    You are an automated Enterprise IAM Governance Agent. Analyze this Okta System Log payload for security anomalies.
    
    Source File Asset: {file_name}
    Log Ingestion Payload:
    {json.dumps(log_payload, indent=2)}

    Output your evaluation report strictly in professional Markdown format:
    # Identity Access & Governance Audit Report
    ## Source Asset: {file_name}
    ## 1. Executive Risk Summary
    ## 2. Flagged Anomalies & Telemetry
    ## 3. Mandatory Remediation Runbook
    """
    print(f"Analyzing {file_name} via Gemini 2.5...")
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    return response.text

def publish_report(report_data, source_file_path):
    """Publishes custom markdown reports matching the naming schema of the source asset."""
    base_name = os.path.splitext(os.path.basename(source_file_path))[0]
    output_path = f"{base_name}_audit_report.md"
    with open(output_path, "w") as f:
        f.write(report_data)
    print(f"[Success] Report published to: {output_path}\n")

if __name__ == "__main__":
    try:
        cli_args = parse_arguments()
        target_path = os.path.abspath(os.path.expanduser(get_target_path(cli_args)))
        
        # Check if target is an entire directory
        if os.path.isdir(target_path):
            # Grab all JSON files inside the folder
            json_files = glob.glob(os.path.join(target_path, "*.json"))
            if not json_files:
                print(f"Operational Notice: No .json files located inside directory: {target_path}")
                exit(0)
                
            print(f"Batch Processing Initialized. Found {len(json_files)} target log files.\n")
            for file_path in json_files:
                try:
                    payload = process_single_payload(file_path)
                    report = execute_ai_governance_audit(payload, os.path.basename(file_path))
                    publish_report(report, file_path)
                except Exception as file_error:
                    print(f"[Skip] Error processing {os.path.basename(file_path)}: {str(file_error)}")
                    
        # Otherwise, process as a single file
        else:
            payload = process_single_payload(target_path)
            report = execute_ai_governance_audit(payload, os.path.basename(target_path))
            publish_report(report, target_path)
            
    except errors.APIError as api_err:
        print(f"Gemini API Failure: {api_err}")
    except Exception as error:
        print(f"\n[!] Pipeline Execution Error: {str(error)}")