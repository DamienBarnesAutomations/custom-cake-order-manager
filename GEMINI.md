# GEMINI.md

## Project Overview
The **Custom Cake Order Manager** is a sophisticated, automated order intake and management system designed for bespoke bakeries. It leverages AI (LLMs) to transform unstructured natural language (from Telegram/WhatsApp) into structured, validated cake orders. The system bridges the gap between conversational AI and rigid culinary business rules (e.g., structural integrity of tiered cakes).

## Tech Stack
- **Frontend:** Vue.js 3 (Composition API), Vite, Pinia, Vue Router, Tailwind CSS, Lucide Icons.
- **Backend:** Python (FastAPI), Pydantic, Uvicorn.
- **Automation & Orchestration:** n8n (Workflow automation), Gemini/Claude/Groq (LLMs).
- **Database:** PostgreSQL 15 (Relational with JSONB support).
- **Infrastructure:** Docker Compose, Traefik (Reverse proxy with TLS via Cloudflare DNS challenge), Nginx (Static image server).

## Project Structure
- `custom_cake_frontend/`: Admin dashboard for monitoring chat sessions and reviewing orders.
  - `src/views/`: Main pages (Chat, History, Review, Upcoming).
  - `src/services/api.ts`: Axios configuration for backend communication.
- `python_app/`: Core business logic and validation engine.
  - `handlers/cake_order_manager_handler.py`: API endpoints for order validation.
  - `utils/cake_order_validator.py`: **Critical File.** Contains the complex logic for enforcing business rules (lead time, tier sizing, menu options).
- `n8n/`: Automation workflows.
  - `n8n-workflows/`: Exported JSON workflows and initialization scripts.
  - `flows/`: Persistent state for the n8n container.
- `postgres/`: Database configuration.
  - `postgres-init/`: SQL scripts for schema and initial data (`04_00_custom_order_database.sql` is the primary schema).
- `public/images/`: Directory for storing order-related images (synced across containers).

## Core Workflows
1. **Intake:** A message from a bot (Telegram/WhatsApp) triggers an n8n webhook.
2. **Extraction:** n8n sends the message + conversation history to an LLM to extract field updates.
3. **Validation:** Extracted JSON is sent to the Python `python_app/api/cakeOrder/validate` endpoint.
4. **Feedback:** The validator returns updated state, missing fields, or validation errors (e.g., "Tier 2 must be smaller than Tier 1").
5. **Persistence:** Validated data is stored in the `custom_orders` table (PostgreSQL).
6. **Review:** Admins use the Vue.js dashboard to review, price, and accept/reject orders.

## Coding Conventions & Patterns
- **API Versioning:** Currently standard paths under `/api`.
- **Validation:** Business rules are deterministic and implemented in Python, not by the LLM.
- **State Management:** Frontend uses Pinia; Backend is stateless, relying on PostgreSQL for persistence.
- **Logging:** Python uses standard `logging` with a consistent format; n8n logs to the `chat_logs` table.
- **Schema:** Uses JSONB for `selections` in `custom_orders` to allow flexible, evolving order structures.

## Development & Deployment
- **Local Dev:**
  - Frontend: `cd custom_cake_frontend && npm install && npm run dev`
  - Backend: `cd python_app && pip install -r requirements.txt && uvicorn app:app --reload`
- **Production (Docker):**
  - Use `docker-compose up --build -d`
  - Ensure `.env` is populated with necessary API keys (Gemini, Telegram, Cloudflare, etc.).

## Protected Files & Directories
- **DO NOT MODIFY** contents of `.git/`, `postgres/db-data/`, or `letsencrypt/`.
- **BE CAUTIOUS** when modifying `python_app/utils/cake_order_validator.py` as it contains complex nested validation logic.
- **N8N Flows:** Manual changes to `n8n/flows/` may be overwritten by container updates; use `n8n-workflows/` for versioned exports.

## Key Environment Variables
- `GEMINI_API_KEY`: For AI extraction.
- `DOMAIN_OR_IP`: For routing and TLS.
- `POSTGRES_PASSWORD`: Database security.
- `CAKE_ORDER_TELEGRAM_BOT_TOKEN`: Bot connectivity.
