# 🛠️ AI Incident Copilot

Enterprise AI Incident Copilot powered by RAG (Retrieval-Augmented Generation), OpenAI, Vector Search and AI Observability.

The project simulates a modern enterprise AI assistant capable of analyzing logs, incidents and technical documentation to help engineers troubleshoot production issues.

---

# 🚀 Features

## Current Features

- Upload `.txt` and `.log` files
- Semantic search using embeddings
- RAG-based question answering
- OpenAI integration
- Conversation history
- Feedback collection (👍 / 👎)
- AI observability metrics
- SQLite interaction persistence
- Streamlit interactive UI

---

# 🧠 Architecture

```text
User
 ↓
Streamlit UI
 ↓
RAG Pipeline
 ↓
Embeddings
 ↓
Vector Database (ChromaDB)
 ↓
LLM (OpenAI)
 ↓
Response + Metrics + Feedback
```

---

# ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| AI Framework | LangChain |
| LLM | OpenAI GPT-4.1-mini |
| Embeddings | text-embedding-3-small |
| Vector DB | ChromaDB |
| Persistence | SQLite |
| Language | Python |
| Observability | Custom Metrics Dashboard |
| Version Control | Git + GitHub |

---

# 📚 What I Learned

This project was created to learn and simulate enterprise-grade GenAI architectures similar to modern internal AI copilots used in large organizations.

Main learning areas:

- RAG architectures
- Vector databases
- Semantic search
- Embeddings
- Prompt engineering
- AI observability
- LLM interaction logging
- Feedback loops
- Incident analysis workflows
- Enterprise AI patterns

---

# 🔍 Example Questions

```text
What does IJ031070 STATUS_MARKED_ROLLBACK mean?

Why is this datasource transaction failing?

What are the probable causes of this SSLHandshakeException?

Which evidence in the log suggests a timeout issue?
```

---

# 📊 AI Observability Metrics

The application tracks:

- Total interactions
- Average latency
- Positive feedback
- Negative feedback
- Interactions without feedback
- Conversation history

This simulates modern enterprise AI observability and monitoring workflows.

---

# 📂 Project Structure

```text
ai-incident-copilot/
│
├── app/
│   ├── main.py
│   ├── prompts.py
│   ├── database.py
│
├── data/
│
├── docs/
│
├── requirements.txt
├── README.md
├── .env.example
└── .gitignore
```

---

# 🛠️ Local Setup

## 1. Clone repository

```bash
git clone https://github.com/YOUR_USER/ai-incident-copilot.git
cd ai-incident-copilot
```

## 2. Create virtual environment

```bash
py -m venv .venv
```

Activate:

```bash
.\.venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create `.env`

```env
OPENAI_API_KEY=your_api_key
```

## 5. Run application

```bash
streamlit run app/main.py
```

---

# 🧭 Roadmap

## Completed

- [x] Initial RAG MVP
- [x] ChromaDB integration
- [x] OpenAI integration
- [x] SQLite persistence
- [x] Feedback system
- [x] AI observability metrics
- [x] Automatic incident classification

## In Progress

- [ ] Advanced observability dashboard
- [ ] Docker support
- [ ] GitHub Actions CI
- [ ] Kafka-based log ingestion
- [ ] AWS deployment
- [ ] Multi-user support

---

# ☁️ Future Cloud Architecture

Planned cloud architecture:

```text
Frontend
 ↓
Spring Boot API
 ↓
Python RAG Service
 ↓
Vector Database
 ↓
LLM Provider
 ↓
Observability Layer
```

Potential cloud services:

- AWS Lambda
- API Gateway
- DynamoDB
- S3
- ECS/App Runner
- CloudWatch

---

# 📌 Goals

This project aims to simulate real-world enterprise AI solutions focused on:

- AI-powered incident management
- Technical troubleshooting
- Enterprise RAG architectures
- AI observability
- Knowledge retrieval systems
- Production support copilots

---
