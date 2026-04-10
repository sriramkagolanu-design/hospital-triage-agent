from openai import OpenAI
import json

from tools.tool_definitions import tools
from tools.mcp_tools import get_available_beds, get_available_doctors
from utils.logger import log, log_error

client = OpenAI()


def allocation_agent(triage_output):

    log("Running allocation agent")

    # -----------------------------
    # STRICT TRIAGE VALIDATION
    # -----------------------------
    VALID_TRIAGE = ["Critical", "Urgent", "Stable"]

    if not triage_output or "triage_level" not in triage_output:
        return {
            "bed_assigned": None,
            "doctor_assigned": None,
            "reasoning": "Invalid triage input"
        }

    if triage_output["triage_level"] not in VALID_TRIAGE:
        return {
            "bed_assigned": None,
            "doctor_assigned": None,
            "reasoning": "Invalid or unsupported triage level"
        }

    # -----------------------------
    # PROMPT
    # -----------------------------
    prompt = f"""
    You are a hospital resource allocation assistant.

    Triage Output:
    {triage_output}

    Rules:
    - Critical → ICU + Cardiologist
    - Urgent → General bed + General Physician
    - Stable → General bed + General Physician

    Tasks:
    1. Decide required bed_type (ICU or General)
    2. Decide doctor_speciality

    Then use available tools to fetch:
    - available beds
    - available doctors

    Then assign:
    - one bed
    - one doctor

    IMPORTANT:
    - You MUST call tools before answering
    - You MUST return ONLY valid JSON
    - Do NOT return empty response

    Output format:
    {{
        "bed_assigned": "...",
        "doctor_assigned": "...",
        "reasoning": "..."
    }}
    """

    # -----------------------------
    # FIRST CALL (TOOL SELECTION)
    # -----------------------------
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    # -----------------------------
    # HANDLE TOOL CALLS
    # -----------------------------
    if message.tool_calls:

        tool_messages = []

        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            log(f"Tool called: {function_name} with {arguments}")

            if function_name == "get_available_beds":
                result = get_available_beds(**arguments)

            elif function_name == "get_available_doctors":
                result = get_available_doctors(**arguments)

            else:
                result = []

            tool_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

        # -----------------------------
        # SECOND CALL (FINAL RESPONSE)
        # -----------------------------
        follow_up = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt},
                message,
                *tool_messages
            ]
        )

        final_message = follow_up.choices[0].message
        content = final_message.content

        # -----------------------------
        # SAFE PARSING
        # -----------------------------
        if not content:
            log_error("Empty response from LLM")

            return {
                "bed_assigned": None,
                "doctor_assigned": None,
                "reasoning": "LLM returned empty response"
            }

        try:
            result = json.loads(content)
            log(f"Allocation result: {result}")
            return result

        except Exception as e:
            log_error(f"JSON parsing failed: {str(e)}")

            return {
                "bed_assigned": None,
                "doctor_assigned": None,
                "reasoning": content
            }

    # -----------------------------
    # FALLBACK (NO TOOL CALL)
    # -----------------------------
    log_error("No tool was called by LLM")

    return {
        "bed_assigned": None,
        "doctor_assigned": None,
        "reasoning": "Tool calling failed"
    }