# Frontend

Frontend for `Archerion` is built with Next.js App Router and TypeScript.

## Routes

Public:

- `/` - landing page
- `/catalog` - searchable catalog
- `/book/[id]` - book details
- `/login` - sign in
- `/register` - reader registration

Reader:

- `/reader`
- `/reader/loans`
- `/reader/reservations`
- `/reader/fines`

Staff:

- `/staff`
- `/staff/issue`
- `/staff/return`

Admin:

- `/admin`
- `/admin/users`
- `/admin/readers`
- `/admin/books`
- `/admin/loans`
- `/admin/audit`

## API Integration

The frontend talks to the backend through `src/lib/api.ts`.

Key client modules:

- `src/lib/auth.ts`
- `src/lib/catalog.ts`
- `src/lib/reader.ts`
- `src/lib/staff.ts`
- `src/lib/admin.ts`

Auth uses backend JWT endpoints and stores access/refresh tokens in browser storage.

## Development

Install dependencies and run the app:

```bash
npm install
npm run dev
```

Linting:

```bash
npm run lint
```

Expected environment variable:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Current State

- The app already includes separate reader, staff, and admin sections.
- `Audit Timeline` exists as an admin page and depends on the backend audit API.
- Role checks are enforced by backend permissions and mirrored in the UI.
