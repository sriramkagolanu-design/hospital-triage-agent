[README.md](https://github.com/user-attachments/files/26639279/README.md)
# 🏥 Hospital Triage & Resource Allocation System (Agent-Based)

## 📌 Overview

This project implements an **agent-based healthcare triage and resource allocation system** using LLMs and tool integrations.

The system:

* Classifies patient severity (Triage Agent)
* Allocates hospital resources (Allocation Agent)
* Uses **guardrails**, **tool calling**, and **multi-step orchestration (LangGraph)**

---

## 🧠 Architecture

```
Input → Input Guard Agent → Triage Agent (LLM)
      → Human Review (Optional)
      → Allocation Agent (LLM + Tools)
      → MCP Tools (Database)
      → Final Output
```

### 🔹 Sub-agents

* Input Guard Agent (validation & sanitization)
* Vitals Analyzer (LLM)
* Symptoms Analyzer (LLM)
* Risk Aggregator (LLM)
* Allocation Agent (LLM + tools)

---

## ⚙️ Features

* ✅ Multi-step agent pipeline (LangGraph)
* ✅ Input & output guardrails
* ✅ LLM-based reasoning
* ✅ Tool/MCP integration with database
* ✅ Human-in-the-loop override
* ✅ Scenario testing (multiple paths)
* ✅ Evaluation framework (accuracy + reasoning score)

---

## 📁 Project Structure

```
project/
│
├── agents/
│   ├── triage_agent.py
│   ├── allocation_agent.py
│   ├── input_guard_agent.py
│   └── validator_agent.py
│
├── prompts/
│   └── triage_prompts.py
│
├── tools/
│   ├── tool_definitions.py
│   └── mcp_tools.py
│
├── pipeline/
│   └── langgraph_pipeline.py
│
├── evaluation/
│   ├── evaluate.py
│   └── dataset.json
│
├── utils/
│   ├── logger.py
│   └── guardrails.py
│
├── hospital.db
└── main.ipynb
```

---

## 🛠️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone <your-repo-url>
cd project
```

---

### 2️⃣ Create virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# OR
source venv/bin/activate  # Mac/Linux
```

---

### 3️⃣ Install dependencies

```bash
pip install openai langgraph
```

(Optional)

```bash
pip install pandas
```

---

### 4️⃣ Set OpenAI API Key

#### Windows (PowerShell)

```bash
setx OPENAI_API_KEY "your_api_key"
```

#### Mac/Linux

```bash
export OPENAI_API_KEY="your_api_key"
```

---

### 5️⃣ Setup database

Run the database initialization script (if not already created):

```bash
python utils/db_setup.py
```

OR ensure `hospital.db` exists in root.

---

## ▶️ Running the System

### 🔹 Run full pipeline

```python
from pipeline.langgraph_pipeline import run_langgraph_pipeline

input_data = {
    "patient_id": "P001",
    "age": 65,
    "symptoms": ["chest pain"],
    "vitals": {"bp": 85, "oxygen": 82, "heart_rate": 120}
}

result = run_langgraph_pipeline(input_data)
print(result)
```

---

## 🧪 Evaluation

Run evaluation for triage agent:

```python
from evaluation.evaluate import evaluate

evaluate()
```

Metrics:

* Accuracy
* Valid Output Rate
* Reasoning Score

---

## 🔍 Scenario Testing

The system includes multiple test scenarios covering:

* Happy path
* Edge cases
* Adversarial inputs
* Failure cases
* Tool-based recovery

Results are displayed in structured table/JSON format.

---

## 🛡️ Guardrails

### Input Guardrails

* Schema validation
* Missing field detection
* Type checking

### Output Guardrails

* JSON structure enforcement
* Valid label restriction
* Fallback for invalid outputs

---

## 🔧 Tool / MCP Integration

The allocation agent uses tools:

* `get_available_beds`
* `get_available_doctors`

These connect to a **SQLite database (hospital.db)**.

---

## 📊 Evaluation Strategy

* **Accuracy** → correctness of triage classification
* **Reasoning Score** → evaluates explanation quality using rubric-based scoring

---

## 🚀 Future Improvements

* Real-time hospital APIs
* Advanced reasoning evaluation (LLM-as-judge)
* UI dashboard
* Multi-hospital routing

---

## 👨‍⚕️ Use Case

This system simulates **real-world hospital triage workflows**, ensuring:

* Patient safety prioritization
* Efficient resource utilization
* Robust handling of invalid/adversarial inputs

---

## 📌 Notes

* Logging can be toggled via `utils/logger.py`
* Human review step can be disabled for automation
* Designed for educational and demonstration purposes

---

## 🏁 Conclusion

This project demonstrates a **complete agentic AI pipeline** combining:

* LLM reasoning
* Tool integration
* Guardrails
* Evaluation

It reflects real-world system design for healthcare decision support.
