# AutoDev - Multi-Agent AI Software Engineering Pipeline

AutoDev is a 100% free, open-source multi-agent software engineering pipeline. It takes natural language requests, writes Python code, evaluates it using a local Machine Learning risk model, executes the code in a sandboxed Docker environment, and autonomously self-heals if the tests fail using an integrated RAG (Retrieval-Augmented Generation) knowledge base.

## Architecture

- **Architect Agent:** Breaks down the user prompt into a structured, step-by-step Pydantic-validated implementation plan.
- **Coder Agent:** Consumes the plan and generates raw Python code alongside a full Pytest suite.
- **QA Reviewer Agent:** Uses a locally trained XGBoost model to evaluate the abstract syntax tree (AST) of the generated code. If the risk is acceptable, it safely triggers execution in an isolated Docker sandbox.
- **Researcher Agent:** A RAG agent connected to a persistent ChromaDB instance. If Docker tests fail, it queries the DB with the error logs to retrieve exact syntax fixes and feeds them back to the Coder.

## Tech Stack

- **Python 3.10**
- **LangGraph & LangChain** for state machine orchestration and agent logic.
- **Docker SDK** for secure, sandboxed code execution.
- **Scikit-learn & XGBoost** for the local AST-based ML bug risk model.
- **ChromaDB** for local vector storage of documentation context.
- **SQLite** for maintaining detailed execution logs.

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd AutoDev
   ```

2. **Set up the virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your API keys:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Initialize Database & Sandbox:**
   The SQLite DB, ChromaDB, and Docker sandbox will be handled automatically upon the first pipeline run.

6. **Start Docker Desktop:**
   Ensure that your local Docker Engine is running and accessible.

## Usage

Run the main orchestration script:

```bash
python main.py
```

The pipeline will execute the requested prompt, generate code, test it, and self-heal automatically!
