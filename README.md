# GLPI Ticket Router

GLPI Ticket Router is an automated ticket routing system that sits between GLPI — an open source IT service management platform — and a locally-running language model. When a support ticket is created in GLPI, a webhook triggers the router, which classifies the ticket and assigns it to the correct support group via the GLPI REST API. The routing groups and LLM configuration are managed through a built-in admin dashboard, making the system configurable without touching code.

---

## Stack

- **Built with:** FastAPI, SQLAlchemy, SQLite, httpx, Docker Compose
- **LLM providers supported:** Ollama, LM Studio, vLLM, llama.cpp — switchable from the dashboard without code changes
- **Notable:** full stack (GLPI + MariaDB + ticket router) runs with a single `docker compose up`

---

## Architecture

When a ticket is created in GLPI, a configured webhook fires a POST request to the router's `/glpi` endpoint. The endpoint immediately returns a 200 OK to GLPI and places the ticket body onto an internal queue — decoupling the webhook response from the processing time of the language model. A dedicated worker thread pulls tickets off the queue one at a time, sends the ticket content to the configured LLM via its OpenAI-compatible API, parses the routing decision from the JSON response, and writes the group assignment back to GLPI via a PATCH request to the GLPI REST API v1.

**Components:**
- **Webhook endpoint** — receives GLPI webhook, acknowledges immediately, enqueues ticket
- **Queue worker** — dedicated thread that processes tickets sequentially from the queue
- **LLM client** — provider-agnostic HTTP client that calls any OpenAI-compatible inference endpoint
- **Router service** — builds the system prompt from database-stored routing groups and LLM config, calls the LLM client, returns the routing decision
- **Config API** — endpoints for managing routing groups and LLM configuration, consumed by the dashboard
- **Admin dashboard** — first-time setup wizard and ongoing configuration UI

---

## How to run it

**Prerequisites:**
- Docker and Docker Compose
- A locally-running LLM via Ollama, LM Studio, vLLM, or llama.cpp

**Setup:**
```bash
git clone <repo>
cd ticket-router-glpi
cp .env.example .env
# fill in APP_TOKEN and USER_TOKEN in .env
# GLPI_BASE is fixed: http://glpi:80/apirest.php
uv sync  # or pip install -r requirements.txt
```

**Run:**
```bash
docker compose up
```

GLPI will be available at `http://localhost:8080`. The router dashboard is at `http://localhost:8000`.

**First-time setup:**

1. Open the dashboard at `http://localhost:8000`, complete the setup wizard — add routing groups and configure your LLM provider and model name
2. In GLPI, go to Setup → Automatic actions → configure a webhook on ticket creation pointing to `http://ticket-router:8000/glpi` — this works because all services share the same Docker network, no public domain required
3. Note: `glpi_config/local_define.php` is mounted into the GLPI container to allowlist localhost URLs in GLPI's webhook security check — without this GLPI rejects local URLs as unsafe

---

## Key decisions

**Database-driven configuration** — routing groups and LLM parameters (model name, provider, system prompt) are stored in SQLite and read at request time. The alternative was config files or environment variables, but those require a container restart to take effect. With database-driven config, changing the model provider or adding a routing group from the dashboard takes effect immediately on the next ticket — no restart needed.

**SQLAlchemy over raw SQL** — SQLAlchemy's ORM was used instead of raw SQL commands. The reasoning is primarily best practice and learning — the abstraction adds clarity and makes the schema explicit through model definitions rather than scattered SQL strings. For a project this size raw SQL would have been equally valid.

**Queue-based ticket processing** — the original implementation processed tickets directly in the webhook handler. Under concurrent load this caused tickets to be processed out of order or reprocessed when GLPI fired duplicate webhook events. Switching to `queue.Queue` with a dedicated worker thread decouples webhook acknowledgement from processing — GLPI gets its 200 OK immediately, and tickets are processed sequentially in arrival order. The tradeoff is that sequential processing is a throughput bottleneck; a future improvement would be multiple worker threads for parallel processing while maintaining the queue's ordering guarantees.

---

## What's next

- Multiple worker threads for parallel ticket processing — current sequential processing is a throughput bottleneck; multiple workers with the same queue would give the benefits of concurrency while keeping ordering guarantees
- Session token caching — `get_session_token()` makes an HTTP round-trip to GLPI on every ticket; caching with a TTL would eliminate this overhead
- Routing group config caching — routing groups and LLM config are read from SQLite on every ticket; caching these with invalidation on config update would reduce unnecessary DB reads