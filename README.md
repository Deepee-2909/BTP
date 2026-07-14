# DeepRead AI — Legal Risk Detection & RAG Q&A System

An AI-powered system that ingests documents (PDF, DOCX, PPTX, Excel, Images, ZIP archives, and web pages), builds a hybrid search index, and provides two core capabilities:

1. **General RAG Q&A** — Ask questions about any uploaded document and get accurate, context-grounded answers.
2. **Legal Risk Detection** — Automatically scans sponsorship/commercial agreements for risky, ambiguous, or one-sided clauses across 10 risk categories.

## Architecture

```
Document → Extract Text → Chunk → Embed (NVIDIA NV-EmbedQA) → Store (Astra DB)
                                      ↓
                              Build Inverted Index (Keywords)
                                      ↓
Query → Hybrid Retrieval (Semantic + Keyword) → Cross-Encoder Reranking → LLM Answer (Llama 3.3)
```

### Key Components

| Component | Technology |
|-----------|-----------|
| LLM (Q&A + Risk Analysis) | Meta Llama 3.3 70B via NVIDIA NIM |
| Vision OCR | Meta Llama 3.2 90B Vision via NVIDIA NIM |
| Embeddings | NVIDIA NV-EmbedQA 1B v2 (2048-dim) |
| Reranker | BAAI BGE Reranker Base (CrossEncoder) |
| Vector Store | DataStax Astra DB (Cassandra) |
| Caching | Redis (document deduplication) |
| API Framework | FastAPI |
| Translation | Google Translator (auto language detection) |

## Prerequisites

- **Python 3.10+**
- **Redis** — running locally or a hosted instance
- **DataStax Astra DB** — free tier works ([astra.datastax.com](https://astra.datastax.com))
- **NVIDIA API Key** — free credits available ([build.nvidia.com](https://build.nvidia.com))

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/Deepee-2909/BTP.git
cd BTP
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

| Variable | Description |
|----------|-------------|
| `REDIS_URL` | Redis connection URL (default: `redis://localhost:6379`) |
| `ASTRA_DB_API_ENDPOINT` | Your Astra DB API endpoint |
| `ASTRA_DB_APPLICATION_TOKEN` | Your Astra DB application token |
| `NVIDIA_API_KEY` | Your NVIDIA NIM API key (starts with `nvapi-`) |

### 5. Start Redis (if running locally)

```bash
redis-server
```

### 6. Run the API server

```bash
uvicorn api_wrapper:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## API Endpoints

### `POST /hackrx/run` — General RAG Q&A

Send a document URL and a list of questions:

```json
{
  "documents": "https://example.com/report.pdf",
  "questions": [
    "What is the main finding of this report?",
    "What methodology was used?"
  ]
}
```

**Response:**

```json
{
  "job_id": "report-a1b2c3d4",
  "answers": [
    "The main finding is...",
    "The study used a mixed-methods approach..."
  ]
}
```

### `POST /analyze` — Legal Risk Detection

Analyze a contract/agreement for risky clauses:

```json
{
  "document": "https://example.com/sponsorship-agreement.pdf",
  "format": "text"
}
```

Returns a detailed risk report covering 10 categories: termination, exclusivity, liability, IP rights, payment terms, performance obligations, dispute resolution, confidentiality, renewal terms, and morality clauses.

Set `"format": "json"` for structured JSON output.

### `GET /` — Health Check

Returns `{"message": "DeepRead AI - Legal Risk Detection API is live"}`.

## RAG Pipeline Tuning

Both endpoints accept optional parameters to fine-tune retrieval:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `semantic_weight` | 0.7 | Weight for semantic (vector) search results |
| `keyword_weight` | 0.3 | Weight for keyword (inverted index) search results |
| `k_semantic` | 30 | Number of semantic search candidates |
| `k_keyword` | 30 | Number of keyword search candidates |
| `k_rerank` | 15 | Final number of contexts after reranking |

## Project Structure

```
├── worker.py           # Core RAG pipeline, indexing, retrieval, and LLM logic
├── api_wrapper.py      # FastAPI REST API layer
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── .gitignore
```

## Supported Document Formats

| Format | Extensions |
|--------|-----------|
| PDF | `.pdf` |
| Word | `.docx` |
| PowerPoint | `.pptx` |
| Excel | `.xlsx`, `.xls` |
| Images (OCR) | `.jpg`, `.jpeg`, `.png` |
| ZIP Archives | `.zip` (processes all supported files inside) |
| Web Pages | Any URL without a file extension |
