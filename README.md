# 🛡️ Explainable & Risk-Aware Google Workspace Agent

An enterprise-grade **Reasoning and Acting (ReAct)** autonomous agent architecture built natively around the Google GenAI SDK. The system securely orchestrates live integrations across **Gmail, Google Calendar, and Google Tasks** using independent semantic validation layers, automated Explainable AI (XAI) risk auditing, and strict Human-in-the-Loop (HITL) execution intercept gates.

---

## 🚀 Key Architectural Features

* **Custom Hybrid RAG Memory Engine:** Combines sliding-boundary token text chunking (1000 characters, 150 overlap) with a persistent **ChromaDB Vector Store** utilizing `gemini-embedding-001` for dense multi-dimensional text embeddings, mapped via Cosine Similarity.
* **Explainable AI (XAI) Guardrail:** Implements an independent, isolated `XAIGuard` model instance that intercepts every proposed agent tool call to calculate an alignment **Confidence Score** ($0.0$ to $1.0$), evaluate system impact, and log plain-language operational reasoning.
* **Human-in-the-Loop (HITL) Interceptor:** Automatically permits read-only data pulls (`ACCESS` path), but freezes execution and demands manual console user keyboard authorization (`[y/N]`) before allowing any state-changing operations (`MUTATION` path like event inserts or task appends) or high-risk paths to execute.

---

## 📂 Repository Structural Layout

```text
workspace-agent/
│
├── data/
│   └── chroma_db/               # Persistent local vector database files
│
├── src/
│   ├── config/
│   │   └── settings.py          # Type-safe environment variable loader (Pydantic)
│   ├── utils/
│   │   ├── logger.py            # Custom professional system formatting log stream
│   │   └── text_processing.py   # Sliding-boundary HTML clean and chunking utilities
│   ├── api/
│   │   ├── google_auth.py       # Automated live OAuth2 token lifecycle engine
│   │   ├── gemini_client.py     # Resilient text and text-based JSON connection clients
│   │   ├── gmail_client.py      # Gmail REST API attachment and text extractions
│   │   ├── calendar_client.py   # Calendar appointment injection managers
│   │   └── tasks_client.py      # Google Tasks backlog tracker insertions
│   ├── memory/
│   │   ├── email_storage.py     # Document file cache mapping for full email bodies
│   │   └── vector_store.py      # ChromaDB management via gemini-embedding-001
│   ├── xai/
│   │   ├── schemas.py           # Pydantic safety metrics telemetry models
│   │   └── guard.py             # Independent system security auditing layer
│   ├── agents/
│   │   ├── schemas.py           # ReAct step validation format contracts
│   │   └── base_agent.py        # Central reasoning cycle & Human-in-the-Loop gates
│   └── services/
│       └── email_indexer.py     # Incremental background synchronization worker
│
├── tests/                       # Comprehensive integration and validation suites
│   ├── test_auth.py
│   ├── test_memory_rag.py
│   ├── test_agent_reasoning.py
│   └── test_xai_guard.py
│
├── .env                         # Local runtime environment environment variables
├── requirements.txt             # Clean pinned installation dependencies
└── main_autonomous.py           # Interactive central CLI terminal entry point


## 🛠️ Installation & Setup

### 1. Clone the Repository 
```bash
git clone [https://github.com/your-username/workspace-agent.git](https://github.com/your-username/workspace-agent.git)
cd workspace-agent

### 2. Configure Your Environment Variables
```bash
GEMINI_API_KEY=your_google_ai_studio_api_key
GEMINI_MODEL=your_gemini_model
CHROMA_PERSIST_DIRECTORY=data/chroma_db
CHROMA_COLLECTION_NAME=workspace_rag_memory

### 3. Setup Google Cloud Platform Credentials

* Go to the Google Cloud Console, create a project, and enable the Gmail API, Google Calendar API, and Tasks API.
* Configure your OAuth Consent Screen in Testing status and add your email to the Test Users authorized whitelist.
* Download your OAuth 2.0 Client ID Credentials JSON file, rename it to credentials.json, and place it in your project root directory.

### 4. Install Dependencies
```bash
pip install -r requirements.txt

### 5. Run the main script
```bash
python main_autonomous.py