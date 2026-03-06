# Custom Cake Order Manager

A production-grade order intake and management system designed for custom bakeries. It automates the transition from informal social media inquiries (Telegram/WhatsApp) to structured, validated order data using AI-driven workflows and a human-in-the-loop management dashboard.

## Architecture

```text
                                     +-------------------+
                                     | Telegram/WhatsApp |
                                     +---------^---------+
                                               |
                                               |
         +-------------------+       +---------v---------+       +-------------------+
         |  Vue.js Frontend  |       |        n8n        |       |   Google Gemini   |
         | (Order Management <------->  (Orchestrator &  <------->  (AI Intent &    |
         |    Dashboard)     |       |   Flow Control)   |       |   Extraction)     |
         +---------^---------+       +---------^---------+       +-------------------+
                   |                           |
                   |           +---------------+
         +---------v-----------v-------+       |                 +-------------------+
         |       Traefik Proxy         |       +----------------->  FastAPI Service  |
         |  (SSL & Reverse Routing)    |                         | (Order Validation |
         +---------^-------------------+       +----------------->   Engine)         |
                   |                           |                 +---------^---------+
                   |                           |                           |
             +-----v-----+             +-------v-----------+     +---------v---------+
             |   Bakery  |             |   Nginx Server    |     |    PostgreSQL     |
             |   Staff   |             | (Image Reference) |     |  (Relational DB)  |
             +-----------+             +-------------------+     +-------------------+
```

## Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | Vue 3, Vite, TypeScript | Order management dashboard and real-time customer chat interface. |
| **Workflow Engine** | n8n | Orchestrates AI calls, webhook routing, and business process state machine. |
| **Intelligence** | Google Gemini | Natural Language Processing for intent classification and entity extraction. |
| **Validation API** | FastAPI, Python 3.11 | Executes complex business logic (lead times, structural tier constraints). |
| **Database** | PostgreSQL 15 | Relational storage for chat sessions, order drafts, and configuration. |
| **Reverse Proxy** | Traefik | Dynamic service discovery and automated SSL termination. |
| **Image Server** | Nginx | High-performance serving of customer reference images. |

## Project Structure

```text
.
├── custom_cake_frontend/    # Vue.js source code, components, and views
├── python_app/              # FastAPI service for order validation logic
│   ├── handlers/            # API route definitions
│   └── utils/               # Core validation engine (cake_order_validator.py)
├── n8n/                     # Workflow automation configuration
│   └── n8n-workflows/       # Exported JSON workflows (the "brains")
├── postgres/                # Database initialization and schema
│   └── postgres-init/       # SQL scripts for tables, triggers, and seed data
├── public/                  # Static assets and reference image storage
├── docker-compose.yml       # Multi-container orchestration for all services
├── register_bot_tokens.ps1  # Script to initialize Telegram/WhatsApp webhooks
└── convert_env.ps1          # Utility to sync environment configurations
```

## Quick Start

### Prerequisites
- Docker Desktop or Docker Engine
- Git
- Valid Telegram Bot Token and Google Gemini API Key

### Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd custom-cake-order-manager
   ```

2. **Configure Environment**
   Create a `.env` file in the root directory (referencing `docker-compose.yml` for required keys):
   ```bash
   # Database
   POSTGRES_USER=custom_order_user
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_DB=custom_order
   
   # AI & Messaging
   GEMINI_API_KEY=your_google_gemini_key
   TELEGRAM_BOT_TOKEN=your_telegram_token
   
   # Networking
   DOMAIN_NAME=yourdomain.com
   CF_DNS_API_TOKEN=your_cloudflare_token (for SSL)
   ```

3. **Launch Services**
   ```bash
   docker-compose up -d --build
   ```

4. **Initialize Webhooks**
   ```powershell
   ./register_bot_tokens.ps1
   ```

## How It Works

The system processes orders through a tiered validation pipeline:

1.  **Ingestion**: `n8n/n8n-workflows/n8n_exports/all_workflows.json` receives a webhook from Telegram/WhatsApp.
2.  **Intent Classification**: The "Extract Intent" workflow uses Gemini to determine if the user is starting a `NEW_ORDER`, providing a `CHANGE_ORDER`, or asking for `HELP`.
3.  **Entity Extraction**: For order-related intents, Gemini extracts structured fields (flavors, tiers, dates) from the chat history.
4.  **Rigorous Validation**: The workflow POSTs the extracted data to `python_app/utils/cake_order_validator.py`.
    - **Lead Time Check**: Ensures `event_date` is at least 7 days in the future.
    - **Structural Rules**: Validates that multi-tier cakes follow base-size requirements (e.g., 3-tiers require a 10" base).
    - **Dependency Check**: Ensures `delivery_address` is provided if `delivery` is true.
5.  **State Management**: Validated data is upserted into the `custom_orders` table via PostgreSQL triggers.
6.  **Response Generation**: If data is missing or invalid, `Handle Incomplete Order` uses Gemini to generate a friendly, low-friction request for the specific missing information.
7.  **Human Review**: Once an order is complete, it appears in the Vue.js dashboard under `Awaiting Review` for final staff approval.

## Design Decisions

- **Workflow Engine vs. Hardcoded Logic**: Used n8n for high-level orchestration to allow non-technical staff to adjust conversational flows without touching Python code.
- **Python for Validation**: Decoupled business rules into a dedicated FastAPI service because complex structural dependencies (like tier sizing logic) are more maintainable and testable in Python than in n8n's JavaScript nodes.
- **Stateless Extraction**: Gemini is tasked with returning the *full current state* of an order on every turn, rather than just "diffs." This prevents state drift and allows the AI to self-correct if a customer changes their mind mid-conversation.
- **Consolidated Field Schema**: Unified fields like `frosting_flavor` across different order types (cakes vs. cupcakes) instead of creating type-specific duplicates. This reduces the token overhead in AI prompts and simplifies the validation logic by maintaining a single source of truth for shared attributes.

## What This Demonstrates

- **AI Integration**: Practical application of LLMs for structured data extraction and stateful conversation.
- **Microservices Orchestration**: Managing a heterogeneous stack (Vue, FastAPI, n8n, Postgres, Traefik) via Docker Compose.
- **Complex Business Logic**: Implementing strict, multi-dependent validation rules in a production-ready backend.
- **Full-Stack Development**: Delivering a complete lifecycle from customer-facing messaging to administrative management UI.
- **Infrastructure as Code**: Automated environment setup, proxy routing, and SSL management.
