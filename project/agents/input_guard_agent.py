# -----------------------------
# INPUT GUARD AGENT
# -----------------------------

REQUIRED_FIELDS = ["patient_id", "symptoms", "vitals"]
REQUIRED_VITAL_FIELDS = ["bp", "oxygen", "heart_rate"]


def run_input_guard_agent(input_data):
    """
    Validates and sanitizes input before passing to pipeline
    """

    # -----------------------------
    # STRUCTURE VALIDATION
    # -----------------------------
    if not isinstance(input_data, dict):
        return {"status": "invalid", "error": "Input must be a dictionary"}

    for field in REQUIRED_FIELDS:
        if field not in input_data:
            return {"status": "invalid", "error": f"Missing required field: {field}"}

    # -----------------------------
    # SYMPTOMS VALIDATION
    # -----------------------------
    if not isinstance(input_data.get("symptoms"), list):
        return {"status": "invalid", "error": "Symptoms must be a list"}

    # -----------------------------
    # VITALS VALIDATION
    # -----------------------------
    vitals = input_data.get("vitals")

    if not isinstance(vitals, dict):
        return {"status": "invalid", "error": "Vitals must be a dictionary"}

    if not vitals:
        return {"status": "invalid", "error": "Vitals cannot be empty"}

    valid_fields_present = any(field in vitals for field in REQUIRED_VITAL_FIELDS)

    if not valid_fields_present:
        return {"status": "invalid", "error": "Vitals missing required measurements"}

    for key, value in vitals.items():
        if not isinstance(value, (int, float)):
            return {"status": "invalid", "error": f"Invalid type for {key}"}

    # -----------------------------
    # PASSED
    # -----------------------------
    return {
        "status": "valid",
        "data": input_data,
        "message": "Input validation successful"
    }