# pipeline/langgraph_pipeline.py

from langgraph.graph import StateGraph, END

from agents.input_guard_agent import run_input_guard_agent
from agents.triage_agent import run_triage_agent
from agents.allocation_agent import allocation_agent as run_allocation_agent


# -----------------------------
# NODE DEFINITIONS
# -----------------------------

def guard_node(state):
    result = run_input_guard_agent(state["input"])

    if result["status"] != "valid":
        return {"input": state["input"], "error": result["error"]}

    return {"input": state["input"]}


def triage_node(state):
    result = run_triage_agent(state["input"])

    return {
        "input": state["input"],
        "triage": result
    }


def human_review_node(state):
    """
    TERMINAL-BASED HUMAN-IN-THE-LOOP
    """

    triage = state["triage"]

    print("\n🧑‍⚕️ AI TRIAGE RESULT:")
    print(triage)

    choice = input("👉 Do you want to override? (yes/no): ")

    if choice.lower() == "yes":
        new_level = input("👉 Enter new triage level (Critical/Urgent/Stable/Invalid): ")

        triage["triage_level"] = new_level.capitalize()

        return {
            **state,
            "triage_final": triage,
            "human_override": True
        }

    return {
        **state,
        "triage_final": triage
    }


def allocation_node(state):
    triage = state.get("triage_final")

    if not triage or "triage_level" not in triage:
        return {**state, "error": "Invalid triage output"}

    result = run_allocation_agent(triage)

    return {
        **state,
        "allocation": result
    }


# -----------------------------
# GRAPH BUILDING
# -----------------------------

def build_graph():
    builder = StateGraph(dict)

    builder.add_node("guard", guard_node)
    builder.add_node("triage", triage_node)
    builder.add_node("human_review", human_review_node)
    builder.add_node("allocation", allocation_node)

    builder.set_entry_point("guard")

    # Guard routing
    def guard_router(state):
        if state.get("error"):
            return END
        return "triage"

    builder.add_conditional_edges("guard", guard_router)

    # 🔥 NEW: triage routing
    def triage_router(state):
        triage = state.get("triage", {})

        if triage.get("triage_level") == "Invalid":
            return END

        return "human_review"

    builder.add_conditional_edges("triage", triage_router)

    # Flow
    builder.add_edge("human_review", "allocation")

    builder.add_edge("allocation", END)

    return builder.compile()


# -----------------------------
# RUN FUNCTION
# -----------------------------

def run_langgraph_pipeline(input_data):
    graph = build_graph()

    result = graph.invoke({
        "input": input_data
    })

    return result