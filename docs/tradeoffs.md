# Design trade-offs

- **SQLite:** very easy to run locally and adequate for a demo; PostgreSQL is a better fit for production concurrency and managed hosting.
- **Server-side pagination:** avoids returning all 10,000 records for every table refresh.
- **Soft deactivation:** preserves historical employee records rather than permanently deleting them.
- **Currency separation:** salary totals are grouped by currency because adding INR, USD, EUR, and other amounts without FX conversion is misleading.
- **Synthetic records:** protect privacy and make the seed process repeatable.
- **No authentication in this starter:** kept out of the first implementation to focus on the requested core workflow. A real salary system must add role-based access control, secure sessions, audit trails, and encryption.
