# Citta — Public Architecture Blueprint

> *"Knowledge is not a static state, but a continuous process of arising and ceasing."*

Citta (จิต — Pali/Sanskrit: *mind/consciousness*) is a **zero-waste, distributed AI ecosystem** designed for continuous web intelligence and cognitive processing. It orchestrates Local LLMs, persistent Data Lakes, and low-power Edge Scrapers into a unified *Stream of Consciousness*.

---

## What It Does

Citta sits between your IDE or any OpenAI-compatible client and your upstream LLM providers. Instead of sending raw prompts directly to a model, every request passes through Citta's **Prompt Firewall**, which:

- Strips sycophantic, verbose, or off-brand LLM defaults
- Injects a consistent, opinionated system directive
- Routes to the best available backend (Gemini, OpenAI, DeepSeek, or any LiteLLM-supported model)
- Returns a standard OpenAI-schema response — invisible to the caller

Your IDE sees a local endpoint. Citta handles everything else.

---

## System Architecture

```
┌──────────────────────────────────────────────────────┐
│  Any OpenAI-compatible client                        │
│  (IDE / Kilo Code / Copilot / curl)                  │
└────────────────────┬─────────────────────────────────┘
                     │  POST /v1/chat/completions
                     ▼
┌──────────────────────────────────────────────────────┐
│  Node 1 — Citta Proxy Gateway                        │
│  FastAPI  +  LiteLLM  +  Docker                     │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  Prompt Firewall                              │   │
│  │  Strip user overrides → Inject directive      │   │
│  │  Resolve model alias → Route to backend       │   │
│  └──────────────────────────────────────────────┘   │
└────────────────────┬─────────────────────────────────┘
                     │
       ┌─────────────┼──────────────┐
       ▼             ▼              ▼
  Gemini API    DeepSeek API    OpenAI API
  (Google)      (deepseek.com)  (openai.com)
```

*(Future nodes: Redis broker on Node 2, Edge Scrapers on Node 3+, Data Lake)*

---

## Technology Stack

| Layer          | Technology                          |
|----------------|-------------------------------------|
| API Framework  | FastAPI 0.109                        |
| LLM Routing    | LiteLLM 1.22                         |
| Runtime        | Python 3.11 (slim)                   |
| Container      | Docker (multi-stage, zero-waste build)|
| Orchestration  | Docker Compose                       |
| Config         | python-dotenv                        |

---

## Quick Start

**Prerequisites:** Docker Desktop, Git

```bash
# 1. Clone
git clone <your-repo-url>
cd Citta

# 2. Configure credentials (copy example, fill in real keys)
cp .env.example .env
# Edit .env and add your API keys

# 3. Start
docker-compose up -d --build

# 4. Verify
curl http://localhost:8000/health
# → {"status": "healthy"}
```

---

## Connecting Your IDE

Configure any OpenAI-compatible IDE plugin (Kilo Code, Copilot, Cursor, Continue, etc.):

| Setting        | Value                          |
|----------------|--------------------------------|
| API Base URL   | `http://localhost:8000/v1`     |
| API Key        | `any-string` (handled by Citta)|
| Model          | `deepseek-chat` or `gemini/gemini-2.0-flash` |

---

## Supported Models

| Model alias you send     | Routed to                    |
|--------------------------|------------------------------|
| `deepseek-chat`          | DeepSeek V3                  |
| `deepseek-reasoner`      | DeepSeek R1                  |
| `gemini/gemini-2.0-flash`| Google Gemini 2.0 Flash      |
| `gemini-1.5-pro`         | Google Gemini 2.0 Flash (aliased) |
| Any other string         | Passed through to LiteLLM    |

---

## Endpoints

| Method | Path                    | Description                              |
|--------|-------------------------|------------------------------------------|
| GET    | `/`                     | Service status                           |
| GET    | `/health`               | Health check                             |
| POST   | `/v1/chat/completions`  | OpenAI-compatible chat completions       |

---

## Design Principles

- **Zero-waste**: Minimal container footprint, no idle compute, no unnecessary data retention  
- **Local-first**: All routing logic runs on your hardware; only inference calls leave the machine  
- **IDE-transparent**: Drop-in replacement for any OpenAI endpoint — no client modifications  
- **Opinionated output**: Consistent, structured, sycophancy-free responses across all models  

---

## Roadmap

- [x] Phase 1 — Proxy Gateway (Node 1): OpenAI-compatible endpoint, multi-model routing, prompt firewall
- [ ] Phase 2 — Message Broker (Node 2): Redis queue on Synology NAS for async processing
- [ ] Phase 3 — Edge Scrapers: Low-power web intelligence nodes feeding the Data Lake
- [ ] Phase 3 — Data Lake: Persistent vector knowledge store for long-term memory

---

## Project Structure

```
Citta/
├── main.py                  # FastAPI app + Prompt Firewall
├── Dockerfile               # Multi-stage zero-waste build
├── docker-compose.yml       # Node 1 container config
├── requirements.txt         # Python dependencies
├── .env.example             # Credential template (copy → .env)
├── .env                     # Live credentials — gitignored, never committed
├── Docs/
│   ├── High-LevelSystemArchitecture.png
│   ├── SequenceDiagram.png
│   ├── CittaLogo.png
│   └── private/             # Local only — gitignored
└── vibecode/                # Engineering work logs
```

---

## Security

- All credentials are stored in `.env` (gitignored)
- A `.env.example` template is provided with placeholder values
- No credentials are stored in Docker image layers (multi-stage build)
- The proxy never logs or forwards credential values

**Never commit `.env`.**  If you accidentally do, rotate all keys immediately.

---

## License

*To be defined by project owner.*
