# ADR 003: SessionFactory as shared database interface

**Context**

Multiple components need database access — the config API reads and writes routing groups and LLM configuration, the router service reads config at ticket processing time, and the seed function writes the default model on startup. The question was how to manage database connections across all these different locations without each one having to know how to create and close a connection.

**Options considered**

- Open a connection per file — each component that needs the database creates its own connection with a hardcoded path. Simple but every component owns connection lifecycle logic, and changing the database location means touching every file.
- Shared `SessionFactory` context manager — one place defines how to create an engine and session. Every other component just uses `with SessionFactory() as session:` and gets a ready connection that closes automatically when the block exits.

**Decision**

`SessionFactory` in `db/sessions.py` wraps SQLAlchemy's session creation behind a context manager. The engine is created once. Any component that needs database access imports `SessionFactory` and uses it with a `with` statement — the session opens on entry and closes automatically on exit, whether the block completes normally or raises an exception. No component needs to know the database path or manage connection lifecycle.

**Consequences**

- Database connection logic lives in one place — changing the database location or engine configuration requires one file change
- Components are decoupled from connection management — they only care about what they query, not how to connect
- The context manager guarantees connections are always closed, preventing connection leaks
- Identified as an improvement over the TLA Advisor approach where SQLite connections were opened with hardcoded paths in multiple places across the codebase
