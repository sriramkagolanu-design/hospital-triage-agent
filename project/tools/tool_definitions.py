# -----------------------------
# TOOL DEFINITIONS (for LLM)
# -----------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_available_beds",
            "description": "Retrieve available hospital beds. Use ICU for critical patients and General for non-critical patients.",
            "parameters": {
                "type": "object",
                "properties": {
                    "bed_type": {
                        "type": "string",
                        "enum": ["ICU", "General"],
                        "description": "Type of bed required"
                    }
                },
                "required": ["bed_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_available_doctors",
            "description": "Retrieve available doctors. Use Cardiologist for critical cases and General Physician for others.",
            "parameters": {
                "type": "object",
                "properties": {
                    "speciality": {
                        "type": "string",
                        "enum": ["Cardiologist", "General Physician"],
                        "description": "Doctor speciality required"
                    }
                },
                "required": ["speciality"]
            }
        }
    }
]