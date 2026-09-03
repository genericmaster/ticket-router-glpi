# ADR 004: FastAPI lifespan for startup orchestration

**Context**

Three things need to exist for the full lifetime of the application — the database schema, a base LLM configuration, and the worker thread. The question was when and how to initialise these so they are ready before the first request arrives and persist for as long as the app is running.

**Options considered**

- Initialise lazily on first request — simpler but introduces delay on the first ticket or dashboard load. The worker thread especially cannot be lazy — if no ticket has arrived yet, the thread isn't running and the queue has no consumer.
- Startup event handlers (`@app.on_event("startup")`) — FastAPI's older pattern for running code at startup. Deprecated in favour of lifespan.
- FastAPI lifespan context manager — a single function that runs startup logic before `yield` and teardown logic after. Everything that needs to exist at runtime is initialised here.

**Decision**

FastAPI's `lifespan` context manager handles three startup tasks in order:

1. `Base.metadata.create_all(engine)` — creates all database tables if they don't exist yet
2. `add_model()` — seeds the `llm_config` table with a default model and provider if it is empty, so the dashboard has a base configuration to show on first load without forcing the user through the wizard for LLM setup
3. `run_in_thread()` — starts the worker thread as a daemon so it is running and waiting to consume from the queue before any ticket arrives

**Consequences**

- The app is fully ready before the first request — no cold-start delay on the first ticket or dashboard load
- The worker thread runs for the full lifetime of the app as a daemon thread — it exits automatically when the main process exits
- The database schema is always up to date at startup — no separate migration step needed for this project's simple schema
- `add_model()` is idempotent — it checks if a config already exists before inserting, so restarting the app never duplicates the seed data