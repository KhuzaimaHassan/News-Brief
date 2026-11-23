# 📰 News Brief — Executive AI Daily Briefing & Memory Agent

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/Flask-3.0.3-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/Oracle-Database_26ai-F80000?style=for-the-badge&logo=oracle&logoColor=white" alt="Oracle DB" />
  <img src="https://img.shields.io/badge/OCI-Generative_AI-C74634?style=for-the-badge&logo=oracle&logoColor=white" alt="OCI GenAI" />
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Render-Cloud_Deploy-46E3B7?style=for-the-badge&logo=render&logoColor=black" alt="Render" />
  <img src="https://img.shields.io/badge/TailwindCSS-DaisyUI-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind CSS" />
</p>

<p align="center">
  <strong>An in-database executive AI briefing engine powered by Oracle Autonomous Database 26ai, OCI Generative AI, and Oracle AI Agent Memory.</strong>
  <br />
  Reads your RSS intelligence streams, connects multi-day story arcs, and synthesizes structured editorial digests in a distinct procedural voice.
</p>

---

> [!NOTE]
> ### 👤 Contributor Note & Engineering Scope
> This project began from an AI engineering masterclass template by **Casius Lee**. The repository includes a Flask application, Oracle database and AI integration, container configuration, and a Render credential-bootstrap script. The project does not include deployment-run evidence that establishes production readiness, zero cost, or comprehensive security review.

---

## 💡 What Makes News Brief Different?

Traditional news aggregators overwhelm you with raw headlines, while generic AI summarizers output detached bullet points. **News Brief** operates as an intelligent memory agent:

1. **Oracle-backed generation and memory:** Article summaries and daily briefings call Oracle `DBMS_CLOUD_AI.GENERATE`; story memory and embedding use `OracleAgentMemory` configured with OCI GenAI clients. This is an Oracle-integrated flow, not a guarantee that all model computation runs inside the database process.
2. **Four-Tier Cognitive Memory:** Automatically links developing stories across days using vector similarity to surface true follow-ups rather than duplicate noise.
3. **Executive Editorial Voice:** Governed by **Procedural Memory** to enforce concise framing: *What Happened*, *Why It Matters*, an *Analogy*, and strategic *Opportunities*.
4. **Cloud credential bootstrap:** The Docker startup script decodes Base64 environment variables into wallet and PEM files before Gunicorn starts. Base64 is encoding, not encryption; the credentials are written to the container filesystem during startup.

---

## 🏛️ Architecture & Data Flow

```mermaid
flowchart TD
    subgraph DataSources [Intelligence Sources]
        RSS[Tech & AI RSS Feeds<br/>OpenAI, DeepMind, Wired, TechCrunch]
    end

    subgraph AppLayer [Flask Web Service / Docker]
        FetchRoute["POST /fetch<br/>FeedParser & Normalization"]
        SumRoute["POST /summarise<br/>Select AI Dispatcher"]
        SaveRoute["POST /save<br/>Vector Similarity Check"]
        BriefRoute["GET /brief<br/>Daily Synthesis Generator"]
        SearchRoute["POST /search<br/>Vector Memory Explorer"]
        SetupScript["render_setup.py<br/>Ephemeral mTLS & PEM Decryption"]
    end

    subgraph OracleCloud [Oracle Cloud Infrastructure]
        subgraph ADB [Oracle Autonomous Database 26ai]
            SelectAI["DBMS_CLOUD_AI<br/>In-DB Chat & Summarization"]
            OAMP_Tables["Oracle AI Agent Memory<br/>Vector Store & Embeddings"]
            mTLS_Conn["mTLS Connection Pool<br/>Thin Mode / cwallet.sso"]
        end
        subgraph OCIGenAI [OCI Generative AI]
            CohereCommand["Cohere Command-R<br/>Synthesis & Summary"]
            CohereEmbed["Cohere Embed-English v3.0<br/>Vector Similarity"]
        end
    end

    subgraph Presentation [Executive UI]
        FeedView["Home / Feed Reader<br/>TailwindCSS & DaisyUI"]
        BriefView["Daily Briefing Reader<br/>Playfair Serif & Luxury Theme"]
        SearchView["Memory Search<br/>Cross-Day History"]
    end

    RSS --> FetchRoute
    FetchRoute --> FeedView
    FeedView --> SumRoute
    SumRoute --> SelectAI
    SelectAI <--> CohereCommand
    FeedView --> SaveRoute
    SaveRoute --> OAMP_Tables
    OAMP_Tables <--> CohereEmbed
    BriefView --> BriefRoute
    BriefRoute --> SelectAI
    BriefRoute --> OAMP_Tables
    SearchView --> SearchRoute
    SearchRoute --> OAMP_Tables
    SetupScript -.->|Unpacks Wallet & PEM| mTLS_Conn
```

---

## 🧠 Cognitive Memory Hierarchy

News Brief leverages `OracleAgentMemory` to maintain distinct memory tiers:

| Memory Tier | Role in Briefing | How It Works |
| :--- | :--- | :--- |
| **Episodic** | Cross-Day Story Linking | Stores each event with timestamp and source. When a new story is parsed, vector distance detects if it's a continuation of a past story and marks it as a follow-up. |
| **Semantic** | World Model & Industry Trends | Tracks key organizations, recurring themes, and broad industry shifts across weeks of reading. |
| **Procedural** | Stylistic & Editorial Voice | Injected style rules: British English, no em dashes, tight narrative hooks, and domain analogies. |
| **Working** | Daily Synthesis Thread | Maintains the active briefing workspace during generation to produce the final top-line digest. |

---

## 🖥️ User Interface & Views

The application provides an editorial experience inspired by luxury print journalism:

* **Executive Dashboard (`/`):** Streamlined feed reader to preview, parse, and selectively summarize raw RSS items.
* **Daily Briefing Reader (`/briefing`):**
  * **TOP LINE:** Flowing synthesized narrative identifying the unifying theme of the day.
  * **5 Top Stories:** Structured breakdown (*What Happened*, *Why It Matters*, *Your Angle*, *Sources*).
  * **Visual Polish:** Drop-cap typography, subtle noise grain texture, and high-contrast editorial styling.
* **Memory Archive & Search (`/search_view`):** Deep semantic search interface to query past stories and briefings stored in the vector database.

---

## 🛣️ API Reference

| Endpoint | Method | Payload / Params | Description |
| :--- | :---: | :--- | :--- |
| `/fetch` | `POST` | `{"url": "<rss_feed_url>"}` | Fetches and parses the latest 20 feed articles. |
| `/summarise` | `POST` | `{"title": "...", "link": "...", "content": "..."}` | Executes `DBMS_CLOUD_AI.GENERATE` inside Oracle for a 2-sentence distillation. |
| `/save` | `POST` | `{"headline": "...", "summary": "..."}` | Performs semantic search for follow-up detection and embeds into Agent Memory. |
| `/brief` | `GET` | *None* | Reads memories, applies procedural rules, and generates the day's 5-story executive briefing. |
| `/search` | `POST` | `{"query": "<text>"}` | Performs vector similarity search across all stored memories. |
| `/past_briefings` | `GET` | *None* | Retrieves all previously generated daily briefings from archive memory. |

---

## 🔐 Render deployment and credential handling

Deploying applications that require **Oracle mTLS Wallets** (`cwallet.sso`, `tnsnames.ora`) and **OCI Private API Keys** (`.pem`) to cloud platforms often leads to accidental credential leaks in Git or requires expensive volume storage.

The Docker image runs `render_setup.py` before Gunicorn. The script decodes `WALLET_BASE64` to `Wallet_newsbrief.zip`, extracts its contents into `./wallet`, and decodes `OCI_KEY_BASE64` to `khuzaima.pem`. These are ordinary files in the container filesystem, not in-memory-only credentials. Base64 does not encrypt or protect a secret. Keep the environment variables restricted to the service, never print their values, and avoid committing source wallet/key files or generated files. Understand the hosting provider's filesystem and redeploy lifecycle before relying on these files.

Configure these Render environment variables from protected values: `DB_USER`, `DB_PASSWORD`, `DB_DSN`, `OCI_USER`, `OCI_TENANCY`, `OCI_FINGERPRINT`, `OCI_COMPARTMENT_ID`, `OCI_REGION`, `WALLET_BASE64`, and `OCI_KEY_BASE64`. Set `OCI_KEY_FILE` only for local use when no decoded `khuzaima.pem` is present. The application and bootstrap script expect `WALLET_LOCATION` (default `./wallet`); the checked-in `.env.example` currently says `WALLET_DIR`, so use `WALLET_LOCATION` in local configuration or align that example separately. The database code uses the wallet password from `DB_PASSWORD`.

The repository does not contain a Render Blueprint or a committed credential encoder, so configure the service's Docker root directory and build/start behavior in the Render dashboard, and use a trusted local tool to prepare encoded file contents. Do not paste secrets into issues, commits, or chat.

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- Python 3.12 (the Dockerfile base image)
- An OCI account and an Oracle Autonomous Database with wallet access
- A database user, DSN, and wallet password
- OCI API signing-key configuration for the memory client
- A Select AI profile named `VIBE_GENAI`; `setup_db.py` contains the SQL and profile setup routine

### 2. Clone Repository
```bash
git clone https://github.com/KhuzaimaHassan/News-Brief.git
cd News-Brief/flask-starter
```

### 3. Configure Environment Variables
Copy the example and provide the database and OCI values:
```bash
cp .env.example .env
```
The app reads `WALLET_LOCATION`, while the current example names this setting `WALLET_DIR`; change the local variable name to `WALLET_LOCATION=./wallet`. Place the extracted Oracle wallet in that directory and set `OCI_KEY_FILE` to a local PEM path. Keep `.env`, wallet files, and private keys out of version control.
```ini
DB_USER=admin
DB_PASSWORD=your_db_password
DB_DSN=newsbrief_high
WALLET_LOCATION=./wallet

OCI_USER=ocid1.user.oc1..xxxxxx
OCI_TENANCY=ocid1.tenancy.oc1..xxxxxx
OCI_FINGERPRINT=xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx
OCI_KEY_FILE=./khuzaima.pem
OCI_COMPARTMENT_ID=ocid1.compartment.oc1..xxxxxx
OCI_REGION=us-chicago-1
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Oracle, seed memory, and launch
```bash
# Create/configure the Select AI profile and database credential
python setup_db.py

# Seed procedural style and sources into Oracle Agent Memory
python seed_style.py
python seed_all.py

# Launch development server
python app.py
```
Visit `http://localhost:5000` in your browser. These commands require a working database, wallet, OCI signing key, and Select AI profile; the app does not provide a local mock mode.

---

## 📦 Container Deployment (Docker)

To run the containerized build locally or deploy to Render:

```bash
docker build -t news-brief -f flask-starter/Dockerfile flask-starter
docker run -p 5000:5000 --env-file flask-starter/.env news-brief
```

---

## 📄 License & Acknowledgments

* **License:** MIT License
* **Core Foundation:** Built upon the AI Developer Advocate Masterclass curriculum by [Casius Lee](https://github.com/casius-connect).
* **Architecture & Cloud Modernization:** [Khuzaima Hassan](https://github.com/KhuzaimaHassan).
