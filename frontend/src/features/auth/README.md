# `auth` feature (placeholder)

Authentication is intentionally **not implemented** in this educational MVP — it
is a public demo. This module exists to show where auth *would* live in the
modular feature architecture, so it could be added without touching other
features.

A production build would add here:

- `services/authService.ts` — login / token refresh against the backend.
- `hooks/useAuth.ts` — React Query + a Zustand auth slice for the session.
- `pages/LoginPage.tsx` — the login screen.
- `components/` — forms, route guards (`<RequireAuth>`).

The backend already ships a `User` entity and a `core/security.py` seam for the
matching server-side work.
