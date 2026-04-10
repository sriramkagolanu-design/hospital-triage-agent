import json
import re
from agents.triage_agent import run_triage_agent


# -----------------------------
# CONFIG
# -----------------------------
REQUIRED_FIELDS = ["triage_level", "reasoning"]
VALID_LABELS = ["Critical", "Urgent", "Stable", "Invalid"]


# -----------------------------
# OUTPUT VALIDATION
# -----------------------------
def validate_output(output):
    if not isinstance(output, dict):
        return False, "Output is not a dictionary"

    for field in REQUIRED_FIELDS:
        if field not in output:
            return False, f"Missing field: {field}"

    if output["triage_level"] not in VALID_LABELS:
        return False, f"Invalid triage level: {output['triage_level']}"

    return True, "Valid"


# -----------------------------
# HELPER: CHECK NUMERIC PRESENCE
# -----------------------------
def contains_number(text):
    return bool(re.search(r"\d+", text))


# -----------------------------
# IMPROVED REASONING EVALUATION
# -----------------------------
def evaluate_reasoning(output, input_data):

    reasoning = output.get("reasoning", "").lower()

    if not reasoning:
        return 0

    score = 0
    checks = 0

    vitals = input_data.get("vitals", {})
    symptoms = input_data.get("symptoms", [])

    # -----------------------------
    # BP CHECK (more flexible)
    # -----------------------------
    if "bp" in vitals:
        checks += 1
        if vitals["bp"] < 90:
            if any(word in reasoning for word in [
                "bp", "blood pressure", "low", "below"
            ]):
                score += 1

    # -----------------------------
    # OXYGEN CHECK (more flexible)
    # -----------------------------
    if "oxygen" in vitals:
        checks += 1
        if vitals["oxygen"] < 90:
            if any(word in reasoning for word in [
                "oxygen", "spo2", "saturation", "low", "below"
            ]):
                score += 1

    # -----------------------------
    # SYMPTOM CHECK (more flexible)
    # -----------------------------
    if symptoms:
        checks += 1
        if any(
            symptom.lower() in reasoning or
            "symptom" in reasoning
            for symptom in symptoms
        ):
            score += 1

    return score / checks if checks > 0 else 1

# -----------------------------
# MAIN EVALUATION
# -----------------------------
def evaluate():

    with open("evaluation/dataset.json", "r") as f:
        dataset = json.load(f)

    correct = 0
    total = len(dataset)

    valid_outputs = 0
    reasoning_scores = []

    print("\n🚀 Running LLM Evaluation...\n")

    for i, case in enumerate(dataset):

        input_data = case["input"]
        expected = case["expected_output"]["triage_level"]

        try:
            result = run_triage_agent(input_data)

            # Validate output
            is_valid, msg = validate_output(result)

            if not is_valid:
                predicted = "Invalid"
                print(f"Case {i+1}: ❌ Invalid Output ({msg})")
            else:
                valid_outputs += 1
                predicted = result["triage_level"]

                reasoning_score = evaluate_reasoning(result, input_data)
                reasoning_scores.append(reasoning_score)

        except Exception as e:
            predicted = "Invalid"
            print(f"Case {i+1}: ❌ Error: {str(e)}")

        # Accuracy check
        if predicted == expected:
            correct += 1
            status = "✅"
        else:
            status = "❌"

        print(f"Case {i+1}: {status}")
        print(f"  Expected: {expected}")
        print(f"  Predicted: {predicted}")

        if predicted != "Invalid":
            print(f"  Reasoning Score: {reasoning_score:.2f}")

        print()

    # -----------------------------
    # FINAL METRICS
    # -----------------------------
    accuracy = correct / total if total > 0 else 0
    validity_rate = valid_outputs / total if total > 0 else 0
    avg_reasoning = (
        sum(reasoning_scores) / len(reasoning_scores)
        if reasoning_scores else 0
    )

    print("------- FINAL RESULT ------")
    print(f"Accuracy: {accuracy:.2f} ({correct}/{total})")
    print(f"Accuracy (%): {accuracy * 100:.1f}%")
    print(f"Valid Output Rate: {validity_rate * 100:.1f}%")
    print(f"Avg Reasoning Score: {avg_reasoning:.2f}")