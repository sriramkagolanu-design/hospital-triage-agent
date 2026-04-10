from openai import OpenAI
import json

from prompts.triage_prompts import (
    VITALS_PROMPT,
    SYMPTOMS_PROMPT,
    RISK_PROMPT
)

from utils.logger import log, log_error, log_input, log_output

client = OpenAI()

# -----------------------------
# OUTPUT VALIDATION
# -----------------------------
VALID_LABELS = ["Critical", "Urgent", "Stable", "Invalid"]

def validate_output(output):
    if not isinstance(output, dict):
        return False, "Output not a dictionary"

    if "triage_level" not in output:
        return False, "Missing triage_level"

    if output["triage_level"] not in VALID_LABELS:
        return False, f"Invalid triage level: {output['triage_level']}"

    if "reasoning" not in output:
        return False, "Missing reasoning"

    return True, "Valid"


# -----------------------------
# Sub-Agent 1: Vitals Analyzer
# -----------------------------
def vitals_agent(vitals):
    log("Running vitals agent")

    prompt = VITALS_PROMPT.format(vitals=vitals)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content

    try:
        result = json.loads(content)
        log(f"Vitals result: {result}")
        return result
    except:
        log_error("Failed to parse vitals response")
        return {"severity": "Unknown", "reasoning": content}


# -----------------------------
# Sub-Agent 2: Symptoms Analyzer
# -----------------------------
def symptoms_agent(symptoms):
    log("Running symptoms agent")

    prompt = SYMPTOMS_PROMPT.format(symptoms=symptoms)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content

    try:
        result = json.loads(content)
        log(f"Symptoms result: {result}")
        return result
    except:
        log_error("Failed to parse symptoms response")
        return {"severity": "Unknown", "reasoning": content}


# -----------------------------
# Sub-Agent 3: Risk Aggregator
# -----------------------------
def risk_agent(vitals_result, symptoms_result):
    log("Running risk aggregation agent")

    prompt = RISK_PROMPT.format(
        vitals_analysis=vitals_result,
        symptoms_analysis=symptoms_result
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content

    try:
        result = json.loads(content)
        log(f"Final triage result (raw): {result}")
        return result
    except:
        log_error("Failed to parse final risk response")
        return {"triage_level": "Invalid", "reasoning": "Invalid model output"}


# -----------------------------
# MAIN TRIAGE AGENT (Orchestrator)
# -----------------------------
def run_triage_agent(input_data):

    # -----------------------------
    # LOG INPUT
    # -----------------------------
    log_input(input_data)

    # -----------------------------
    # EXTRACT DATA
    # -----------------------------
    vitals = input_data.get("vitals", {})
    symptoms = input_data.get("symptoms", [])

    # -----------------------------
    # SUB-AGENT CALLS
    # -----------------------------
    vitals_result = vitals_agent(vitals)
    symptoms_result = symptoms_agent(symptoms)

    # -----------------------------
    # FINAL AGGREGATION
    # -----------------------------
    final_result = risk_agent(vitals_result, symptoms_result)

    # -----------------------------
    # NORMALIZE OUTPUT
    # -----------------------------
    if "triage_level" in final_result:
        final_result["triage_level"] = final_result["triage_level"].capitalize()

    # -----------------------------
    # OUTPUT VALIDATION (OUTPUT GUARDRAIL)
    # -----------------------------
    is_valid_output, message = validate_output(final_result)

    if not is_valid_output:
        log_error(f"Output validation failed: {message}")
        return {
            "triage_level": "Invalid",
            "reasoning": "Invalid model output"
        }

    # -----------------------------
    # LOG OUTPUT
    # -----------------------------
    log_output(final_result)

    return final_result