# ADR 002: GLPI REST API v1 over v2

**Context**

GLPI exposes two REST API versions — v1 (legacy) and v2 (newer, more secure). The router needs to write group assignment back to a ticket via a PATCH request. v2 was the natural first choice given it is the current version.

**Options considered**

- GLPI REST API v2 — current version, more secure authentication model
- GLPI REST API v1 — legacy, simpler authentication via app token and user token

**Decision**

v1 is used. During development, PATCH requests to the v2 API for group assignment fields (`_groups_id_assign`) consistently returned empty response bodies with no error — the request appeared to succeed but no changes were written to the ticket. After investigation this was identified as a known unresolved bug in GLPI v2 affecting specific field writes. The bug is expected to be fixed in v2.3. v1 was confirmed working for the same PATCH operation and is used until the v2 bug is resolved.

**Consequences**

- The system works correctly against GLPI v1
- v1 authentication is less secure than v2 — app token and user token are passed in headers
- Migration to v2 is straightforward once the bug is fixed — the endpoint structure is similar and only the authentication headers change
