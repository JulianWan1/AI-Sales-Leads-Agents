# AI Sales Lead Agent

## Overview

AI Sales Lead Agent is a multi-agent AI system that transforms business context into discovered sales leads, enriched lead intelligence, prioritized opportunities, and actionable outreach strategies.

The project demonstrates how agentic AI workflows can be orchestrated using multiple specialized reasoning stages — each agent performing real web research and applying judgment — rather than relying on a single monolithic prompt.

This MVP focuses on:

- AI orchestration
- explainable reasoning
- structured outputs
- backend persistence

---

# Problem Statement

Sales teams often spend significant time on:

- identifying potential leads
- qualifying prospects
- prioritizing opportunities
- preparing outreach strategies

Much of this process is repetitive, manual, and difficult to scale.

This project explores how agentic AI workflows can automate and augment that process through a multi-stage reasoning pipeline.

---

# Core Features

## Multi-Agent Workflow

The system uses four specialized AI agents, each with access to external tools:

1. **Lead Discovery Agent** — finds real companies via web search
2. **Lead Enrichment Agent** — researches each company in depth
3. **Lead Scoring Agent** — scores and prioritizes leads against a rubric
4. **Outreach Strategy Agent** — crafts personalized outreach for each lead

Each agent receives context, performs specialized reasoning, and enriches the lead object before passing accumulated intelligence downstream.

---

## Stateful Progressive Enrichment

Lead objects grow progressively richer through the pipeline:

```
Discovery        → company name
Enrichment       → contact, budget, qualification signals, research confidence
Scoring          → lead score, priority, score reasoning
Outreach         → strategy, conversation starter, objections, next action
```

Each stage preserves all prior intelligence while adding new contextual information.

---

## True Agentic Behavior

Each agent is agentic or leverages LLM — it faces situations that are hard to predict and makes judgment calls that would be impractical to encode as static rules:

- **Enrichment**: chooses which tool to call (web search vs. website extraction), decides when it has enough data, synthesizes unstructured content into structured fields
- **Scoring**: applies a rubric against qualitative evidence, explains its reasoning
- **Outreach**: decides whether to search for recent news (High priority leads only) and grounds every claim in enrichment data

The orchestrator itself is a deterministic Python function — it does not use an LLM because all its decisions are conditions, not judgments.

---

## Adaptive Re-Enrichment

If a lead scores 40+ but has low research confidence, the pipeline automatically re-enriches it before finalizing the score. This catches promising leads that were initially under-researched.

---

## Explainable AI Outputs

Every lead includes intermediate reasoning:

- `qualification_signals` — specific signals that support or undermine the lead
- `score_reasoning` — the model's explanation for the score it assigned
- `outreach_strategy` — why this channel and angle fits this lead
- `likely_objections` — grounded in the lead's actual budget and situation

---

## Persistence Layer

Pipeline outputs are persisted into PostgreSQL using SQLAlchemy. Leads are deduplicated by company name on save — re-enrichment updates existing records without losing status history.

---

## Dashboard UI

A Streamlit dashboard provides:

- business context input
- lead generation triggers
- lead visualization with filtering
- scoring visibility
- outreach strategy exploration
- stale lead re-enrichment

---

## Operational Logging

Structured logging with execution timing across every agent and tool call, covering:

- per-lead pipeline progress
- tool call arguments and results
- deduplication events
- fallback triggers

---

# Application Flow

```
POST /business-context
  └── Store business context (industry, product, ideal customer)

POST /generate-strategies
  ├── 1. Lead Discovery Agent
  │     ├── LLM iterates: calls search_web until enough leads found (up to 8 iterations)
  │     ├── Python deduplication: normalize names, remove near-duplicates
  │     └── Filter out companies already in the database
  │
  └── 2. Orchestrator (per lead, sequential)
        ├── Lead Enrichment Agent
        │     ├── LLM iterates: search_company, extract_website_content (up to 8 iterations)
        │     └── Returns: contact, budget signal, qualification signals, confidence, sources
        │
        ├── Fallback check (Python)
        │     └── Drop lead if enrichment returned no useful information
        │
        ├── Lead Scoring Agent
        │     ├── Single LLM call: score 0–100 against rubric, assign priority
        │     └── Returns: lead_score, priority, score_reasoning
        │
        ├── Re-enrichment check (Python)
        │     └── If score ≥ 40 AND confidence = low → re-enrich + re-score
        │
        ├── Outreach Strategy Agent
        │     ├── LLM: High priority → search for recent news first, then generate
        │     │         Medium/Low → generate directly from enrichment data
        │     └── Returns: outreach_strategy, conversation_starter, likely_objections, next_action
        │
        └── Sort results by lead_score (descending), persist to PostgreSQL
```

---

# Project Structure

```
app/
├── agents/
│   ├── orchestrator_agent.py       — deterministic pipeline: enrich → score → re-enrich if needed → outreach
│   ├── lead_discovery_agent.py     — agentic: LLM uses search_web tool to find real companies
│   ├── lead_enrichment_agent.py    — agentic: LLM uses search_company + extract_website_content
│   ├── lead_scoring_agent.py       — single LLM call: scores lead against rubric, assigns priority
│   └── outreach_strategy_agent.py  — agentic: LLM optionally searches for news (High priority only)
│
├── api/
│   ├── business_context.py         — POST /business-context: store business context
│   ├── outreach_strategy.py        — POST /generate-strategies: full pipeline trigger
│   └── leads.py                    — GET /leads/, PATCH /leads/{id}/status, POST /leads/re-enrich-stale
│
├── core/
│   └── database.py                 — SQLAlchemy engine, session factory, Base
│
├── db/
│   └── init_db.py                  — create all tables on startup via Base.metadata.create_all
│
├── models/
│   ├── lead.py                     — Lead SQLAlchemy ORM model (all pipeline output fields)
│   └── business_context.py         — BusinessContext ORM model
│
├── schemas/
│   ├── lead.py                     — Pydantic schema for lead validation
│   └── business_context.py         — Pydantic schema for business context input
│
├── services/
│   ├── openai_service.py           — OpenAI client singleton
│   ├── business_context_service.py — create and retrieve business context records
│   ├── lead_persistence_service.py — save_leads: insert new leads, upsert on re-enrichment
│   └── logger.py                   — structured logger configuration
│
├── tools/
│   ├── tavily_search_tool.py       — Tavily /search wrapper (used by discovery agent)
│   ├── web_search_tool.py          — Tavily /search wrapper with company+focus query (used by enrichment + outreach)
│   └── website_scraper_tool.py     — Tavily /extract wrapper: pulls full content from a URL
│
├── utils/
│   └── context_serializer.py       — serialize BusinessContext ORM object to dict for LLM prompts
│
└── main.py                         — FastAPI app: register routers, call init_db on startup

dashboard.py                        — Streamlit UI: context input, lead generation, visualization
requirements.txt
```

---

# Agent Responsibilities

## Lead Discovery Agent

**Agentic** — the LLM decides which searches to run and when it has found enough leads.

- Runs multiple web searches from different angles (geography, company type, industry segment)
- Collects only real company names found in search results
- Caps at 5 leads after Python deduplication
- Deduplication: normalizes names (strips suffixes, punctuation), removes near-duplicates using substring matching and fuzzy similarity (SequenceMatcher ≥ 0.85)

Outputs: `[{ "company": "..." }]`

---

## Lead Enrichment Agent

**Agentic** — the most valuable stage. The LLM reads unstructured web content and synthesizes it into structured intelligence.

- Searches for the company website, funding history, financial signals, and key decision-makers
- Extracts website content when a URL is found
- Sets `research_confidence` based on how much evidence was found
- Returns a fallback object if it hits max iterations with no useful data

Outputs: contact, role, company_summary, specialization, detected_industry, estimated_budget, research_confidence, interest, budget_signal, purchase_likelihood, qualification_signals, recommended_sales_angle, sources

---

## Lead Scoring Agent

**Single LLM call** — scores against a fixed rubric, explains its reasoning.

- 80–100: strong verified lead (clear fit, strong budget signals, high confidence)
- 60–79: moderate opportunity (good fit but incomplete evidence)
- 40–59: weak or incomplete lead
- below 40: low confidence or poor fit

Outputs: lead_score, priority (High/Medium/Low), score_reasoning

---

## Outreach Strategy Agent

**Conditionally agentic** — High priority leads get a web search for recent news to find a timely hook; Medium/Low leads are generated directly from enrichment data.

- Conversation starter must reference a specific detail from enrichment or recent news
- Likely objections are grounded in the lead's actual budget signal and company size
- Recommended next action is specific and actionable

Outputs: outreach_strategy, conversation_starter, likely_objections, recommended_next_action

---

## Orchestrator

**Not an LLM** — a deterministic Python function that sequences the agents with two decision points:

1. Drop lead if enrichment returned no useful information (fallback check)
2. Re-enrich if score ≥ 40 AND research confidence is low

This avoids unnecessary LLM calls for pure if/else logic.

---

# Example Final Lead Output

```json
{
  "company": "Monaco Motors",
  "contact": "Julian Becker",
  "role": "CEO",
  "interest": "Curated luxury car inventory aligned with their stated expansion into the UK market",
  "estimated_budget": 500000,
  "budget_signal": "High — publicly traded, €200M annual revenue",
  "purchase_likelihood": "High",
  "qualification_signals": [
    "CEO role with direct purchasing authority",
    "Stated expansion goals align with product fit",
    "Recent funding round of €50M in 2024"
  ],
  "recommended_sales_angle": "Focus on exclusivity and prestige to match their brand positioning.",
  "lead_score": 92,
  "priority": "High",
  "score_reasoning": "Top-tier budget signal, high confidence enrichment, and strong strategic fit.",
  "outreach_strategy": "Reach out via LinkedIn with a reference to their recent UK expansion announcement.",
  "conversation_starter": "I saw Monaco Motors just announced their UK expansion — curious how you're thinking about inventory sourcing for that market.",
  "likely_objections": ["Existing supplier relationships", "Timeline pressures from expansion"],
  "recommended_next_action": "Send a LinkedIn connection request referencing the UK expansion, then follow up with a brief demo offer."
}
```

---

# Tech Stack

## Backend

- Python
- FastAPI
- OpenAI API (gpt-4.1-mini)
- Tavily API (web search + content extraction)
- SQLAlchemy
- PostgreSQL

## Infrastructure

- Docker + Docker Compose (PostgreSQL + FastAPI services)

## Frontend

- Streamlit

## AI Concepts

- Multi-agent orchestration
- Agentic tool use (LLM-driven tool selection)
- Stateful progressive enrichment
- Explainable AI reasoning
- Adaptive re-enrichment

---

# Running The Project

## 1. Clone Repository

```bash
git clone <your-repo-url>
cd ai-sales-lead-agent
```

## 2. Configure Environment Variables

Create a `.env` file and add:

```env
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key

DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<dbname>

# Required if running via Docker Compose
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_database_name
```

---

## Option A — Docker (Recommended)

Docker Compose starts both the PostgreSQL database and the FastAPI backend together.

**Prerequisites:** Docker and Docker Compose installed.

```bash
docker-compose up --build
```

This will:
- Start a PostgreSQL 17 container on port `5433`
- Build and start the FastAPI container on port `8000`
- Create the database tables automatically on startup

Swagger docs: `http://127.0.0.1:8000/docs`

To stop:

```bash
docker-compose down
```

To stop and delete the database volume:

```bash
docker-compose down -v
```

---

## Option B — Local (Manual)

### 1. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

```bash
# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run FastAPI Backend

Ensure your PostgreSQL instance is running and `DATABASE_URL` in `.env` points to it, then:

```bash
uvicorn app.main:app --reload
```

Swagger docs: `http://127.0.0.1:8000/docs`

---

## Run Streamlit Dashboard

```bash
streamlit run dashboard.py
```

---

# API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/business-context` | Store business context (industry, product, ideal customer) |
| `POST` | `/generate-strategies` | Run full pipeline: discover → enrich → score → outreach |
| `GET` | `/leads/` | List leads with optional filters (industry, priority, status, score range) |
| `PATCH` | `/leads/{id}/status` | Update lead status (new, contacted, replied, qualified, closed, lost) |
| `POST` | `/leads/re-enrich-stale` | Re-run enrichment pipeline for leads not updated in 30+ days |

---

# Current MVP Limitations

## Synthetic Lead Discovery

The LLM generates lead suggestions from web searches, which may return inconsistent or low-quality results depending on the industry and search terms used. This was intentional to validate the pipeline architecture before integrating real lead providers such as Apollo.io or Clearbit.

## No Structured Output Enforcement

Agents return JSON via prompt instruction rather than OpenAI structured outputs. This works reliably in practice but lacks schema validation and retry handling for malformed responses.

---

# Future Improvements

## Real Lead Integrations

- Apollo.io, Clearbit, LinkedIn Sales Navigator
- CRM system integrations

## Structured Output Enforcement

- OpenAI structured outputs with Pydantic schema validation
- Retry handling for malformed responses

## Human Approval Workflows

- Review stages and approval checkpoints before outreach is sent
- Editable outreach strategies in the dashboard

## Retrieval-Augmented Generation (RAG)

- Enhance strategies using internal sales playbooks and customer histories

## Parallel Enrichment

- Process leads concurrently (currently sequential per lead)

## Advanced Observability

- Metrics dashboards, distributed tracing, pipeline analytics

---

# Key Engineering Concepts Demonstrated

- Multi-agent orchestration
- Agentic tool use with LLM-driven decision making
- Deterministic orchestration (code for conditions, LLM for judgment)
- Stateful progressive enrichment
- Explainable AI reasoning
- Backend API architecture (FastAPI)
- ORM modeling and persistence (SQLAlchemy + PostgreSQL)
- Observability and structured logging
- Dashboard visualization (Streamlit)
- Modular system design

---

# License

MIT License
