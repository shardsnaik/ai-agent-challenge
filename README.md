# Agent-as-Coder — LLM-Powered Bank Statement Parser

## 🧠 Overview
This project implements an **LLM-powered autonomous coding agent** capable of writing custom bank statement parsers dynamically using the **Groq API**.  
The agent reads a sample PDF and its corresponding CSV, understands the schema, and generates a working Python parser (`parse(pdf_path) -> pd.DataFrame`) that matches the expected output.

It follows a self-correcting loop:  
**Plan → Generate → Test → Refine (up to 3 attempts)**

---

## ⚙️ Features
- **LLM Integration (Groq API)** — uses `llama-3.1-70b-versatile` to auto-generate code.  
- **Automatic Parser Generation** — creates a new file under `custom_parser/{bank}_parser.py`.  
- **Self-Debugging** — up to 3 retries based on previous error messages.  
- **Automated Testing** — validates parser output via `DataFrame.equals`.  
- **Simple CLI Interface** — works out of the box with `--target <bank_name>`.

---

## 🧩 Folder Structure
```
ai-agent-challenge/
│
├── agent.py                # Main agent file (Groq-powered)
├── custom_parser/          # Auto-generated parsers are saved here
│   └── __init__.py
│
├── data/
│   └── icici/              # Sample data for target bank
│       ├── icici_sample.pdf
│       └── icici_sample.csv
│
├── tests/
│   └── test_icici_parser.py
│
├── requirements.txt
└── README.md
```

---

## 🚀 Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/<your-username>/ai-agent-challenge.git
cd ai-agent-challenge
```

### 2. Install Dependencies
```bash
python -m venv myenv
source myenv/bin/activate      # (use myenv\Scripts\activate on Windows)
pip install -r requirements.txt
```

### 3. Set Up Groq API Key
Get your free API key from [https://console.groq.com/keys](https://console.groq.com/keys)

Then set it as an environment variable:
```bash
export GROQ_API_KEY="gsk_your_api_key_here"   # macOS/Linux
setx GROQ_API_KEY "gsk_your_api_key_here"     # Windows PowerShell
```

### 4. Run the Agent
```bash
python agent.py --target icici
```

This will:
- Read `data/icici/icici_sample.pdf` and its CSV.  
- Ask Groq LLM to generate a parser file.  
- Test it internally and retry if needed.  

### 5. Verify Parser with Tests
```bash
pytest -q
```

If everything passes, you’ll see:
```
✅ DataFrame.equals -> True
1 passed in 3.2s
```

---

## 🧩 Agent Architecture Diagram
```
 ┌───────────────┐
 │    Planner     │
 │ (Reads schema) │
 └───────┬────────┘
         │
         ▼
 ┌───────────────┐
 │  LLM (Groq)   │
 │Generates code │
 └───────┬────────┘
         │
         ▼
 ┌───────────────┐
 │   Executor    │
 │Runs & tests   │
 └───────┬────────┘
         │
         ▼
 ┌───────────────┐
 │   Refiner     │
 │Self-corrects  │
 └───────────────┘
```

---

## 🛠️ Improvements & Extensions
- Add **LangGraph** for structured agentic workflows.  
- Improve **prompt engineering** for more reliable parser generation.  
- Extend to multiple banks automatically.  
- Add caching & memory for faster re-runs.  
- Integrate with **MLflow** or **Weights & Biases** for logging.

---

## 🧾 License
MIT License © 2025 Your Name

---

## 🙋‍♂️ Author Note
This implementation demonstrates a functional baseline within limited time.  
Further refinement (e.g., multi-bank parsing, complex PDF normalization, and advanced self-debug loops) would require about **3–4 additional days** of focused work.
