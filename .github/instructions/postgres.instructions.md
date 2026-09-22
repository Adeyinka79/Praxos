---
applyTo: "**/*.{sql,psql,py,ts,tsx,js,jsx}"
---

# PostgreSQL instructions

- Prefer explicit SQL schema definitions and migrations over ad hoc DDL.
- Use PostGIS types and spatial indexes where geospatial queries are required.
- Keep tenant and project scoping in every query that touches project data.
- Use UUIDs or stable domain IDs for entity references unless existing conventions require otherwise.
- Avoid direct cross-domain joins that bypass service boundaries.
- Use read-only access patterns for analytics or inspection where possible.
- Validate geospatial assumptions and coordinate systems before implementing location logic.
- Add migration and validation checks for schema changes.
