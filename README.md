# News Brief: AI Daily Briefing

> **Contributor Note:** This project was initially built as a master class template by Casius Lee. I (Khuzaima Hassan) cloned the base project and significantly expanded it. My core contributions include completely overhauling the deployment infrastructure, building a secure base64 secret injection pipeline for cloud hosting, resolving Python dependency conflicts, debugging UI regressions, and successfully deploying the backend with Oracle Autonomous Database via OCI integration on Render.

An AI-powered daily briefing app that reads your favourite RSS feeds, writes a "what-happened" and "why-it-matters" on each story, and remembers everything in an Oracle database so you can query it later.

This is not a generic news aggregator. It is a highly personalised briefing written in a specific procedural style (e.g., tailored for a Developer Advocate, complete with analogies and actionable angles), powered entirely by **Oracle Autonomous Database** and **OCI Generative AI**.

---

## 🏗️ Architecture & Tech Stack

This project is built to ensure all AI operations remain securely within the database layer—no third-party AI keys are ever exposed to the frontend.

* **Backend:** Python, Flask, Gunicorn
* **Database:** Oracle Autonomous Database (Always Free Tier)
* **AI & Memory:** Oracle AI Agent Memory (`oracleagentmemory`), OCI Generative AI (Cohere Command-R)
* **Frontend:** HTML, TailwindCSS, DaisyUI (No heavy frontend frameworks)
* **Deployment:** Dockerized for Render.com free tier with a custom secure-secret injection pipeline.

---

## ✨ Key Features

1. **Episodic & Semantic Memory:** Powered by Oracle AI Agent Memory, the app connects related stories across different days, highlighting follow-ups automatically.
2. **In-Database AI Generation:** Uses `DBMS_CLOUD_AI` (Select AI) to generate summaries securely within the database boundary.
3. **Automated Base64 Secret Pipeline:** Since free cloud tiers (like Render) do not support direct file uploads, the deployment infrastructure automatically decodes and extracts the Oracle mTLS `.zip` Wallet and OCI `.pem` private keys from Base64 environment variables in memory at boot time (`render_setup.py`).
4. **Procedural Vibe Checking:** The AI is seeded with a specific voice ("Procedural Memory") to ensure the daily digest is written exactly how the user prefers.

---

## 🛣️ API Routes

The backend operates via a lightweight Flask contract:

* `POST /fetch` — Parses an RSS URL and returns the 20 newest items (No DB interaction).
* `POST /summarise` — Runs in-DB Select AI to generate a 2-sentence "What Happened / Why it matters" summary.
* `POST /save` — Embeds and stores the story in Oracle. Uses vector search to detect if the story is a follow-up to a past event.
* `GET /brief` — Gathers today's stories, pulls semantic trends, and runs a synthesis generation to produce the final daily briefing.
* `POST /search` — Allows semantic search against all past stored stories.

---

## 🚀 Deployment (Render)

This repository is pre-configured for instant deployment on Docker-based cloud platforms like Render.

1. Ensure the **Root Directory** in Render is set to `flask-starter`.
2. Generate a bulk `.env` payload using the local script to encode your Oracle Wallet `.zip` and OCI `.pem` file into secure Base64 strings.
3. Paste the variables into Render's Environment Variables tab using the "Add from .env" feature.
4. The custom `render_setup.py` boot script will unpack the credentials securely during the Docker container startup sequence.

---

## 📚 Masterclass Origins

*The original starter kit included the following design prompt used to seed the initial AI development:*

> **Starter Prompt:**
> I want a personal AI daily briefing app, not a generic news summary, but a briefing written for my role: an AI Developer Advocate at Oracle.
> - I add RSS feeds for the sources I care about.
> - Each day it fetches them, summarises every story, and stores the summaries so I can query them later.
> - On demand it writes a digest: a top-line narrative, a daily theme, and the five most significant stories.
> - Each story: What happened, Why it matters, Your angle (my content, talk, and demo opportunities).
> - Briefings are saved, so I can read past days.
