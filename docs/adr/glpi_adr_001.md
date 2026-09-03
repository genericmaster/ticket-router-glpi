# ADR 001: Queue-based ticket processing

**Context**

The router needs to process incoming tickets from GLPI webhooks and call a language model for each one. The language model call takes several seconds. The question was how to handle the webhook response while the model is processing, and what happens when multiple tickets arrive in quick succession.

**Options considered**

- Process tickets directly in the webhook handler — simple but the webhook response to GLPI would be delayed by however long the model takes. GLPI expects a fast response and may retry or timeout.
- Async background tasks — FastAPI's `BackgroundTasks` was tried first. The problem was that background tasks get cancelled when the response is sent, meaning ticket processing would terminate as soon as the 200 OK was returned.
- Queue with a dedicated worker thread — decouple the webhook acknowledgement from ticket processing entirely. The webhook handler puts the ticket on a queue and returns immediately. A separate thread consumes from the queue sequentially.

**Decision**

`queue.Queue` with a dedicated daemon thread started at application lifespan. The webhook endpoint enqueues the ticket body and returns 200 OK immediately. The worker thread processes tickets one at a time in arrival order. This also naturally handles duplicate webhook events from GLPI — if GLPI fires the same ticket twice, both go onto the queue and are processed in order rather than concurrently, reducing the chance of race conditions on the GLPI side.

**Consequences**

- GLPI always gets a fast response regardless of model processing time
- Ticket processing is sequential — a bottleneck under high ticket volume
- Future improvement: multiple worker threads consuming from the same queue for parallel processing while retaining arrival order guarantees
- Async httpx was replaced with synchronous httpx because async primitives inside a non-async thread don't make sense — the worker runs in a thread, not the event loop
