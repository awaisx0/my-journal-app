
# Journal App — PRD

Personal use · FastAPI / PostgreSQL / SQLAlchemy · v2.0 (multi-user)

## Data Models

**User**

- `id` — UUID, PK
- `email` — unique, required
- `hashed_password` — required
- `is_email_verified` — default false
- `created_at`, `updated_at` — auto
- `deleted_at` — nullable (soft delete)

**JournalBook**

- `id` — UUID, PK
- `user_id` — FK → User, required (owner)
- `name` — required
- `description`, `emoji`, `color` (hex) — optional
- `is_archived` — default false (manual archive toggle, independent of soft delete)
- `created_at`, `updated_at` — auto
- `deleted_at` — nullable (soft delete)

**JournalEntry**

- `id` — UUID, PK
- `journal_book_id` — FK → JournalBook, required
- `title` — optional
- `content` — required
- `mood` — smallint, nullable, range 0–10
- `created_at`, `updated_at` — auto
- `deleted_at` — nullable (soft delete; cascades when parent book is soft-deleted)

## Endpoints

**Auth**

```
POST   /auth/register
POST   /auth/login
POST   /auth/refresh
POST   /auth/verify-email
POST   /auth/logout
```

**Books**

```
GET    /journals
POST   /journals
GET    /journals/{book_id}
PATCH  /journals/{book_id}
DELETE /journals/{book_id}   (soft delete)
```

**Entries**

```
GET    /journals/{book_id}/entries   (paginated)
POST   /journals/{book_id}/entries
GET    /entries/{entry_id}
PATCH  /entries/{entry_id}
DELETE /entries/{entry_id}   (soft delete)
```

All book/entry routes scoped to `current_user`; no cross-user access. No book sharing in v1.

## Design Decisions (resolved)

- **IDs**: UUID (v4 or v7 — v7 preferred for time-sortable index locality)
- **Migrations**: Alembic from day one
- **Timestamps**: `timestamptz`, UTC
- **Deletes**: soft delete everywhere (`deleted_at`), cascades book → entries
- **Archive**: separate, independent concept from soft delete (`is_archived` flag)
- **Cascade on book delete**: entries soft-deleted alongside parent book
- **Mood**: optional, smallint, 0–10
- **Pagination**: limit/offset style, on entries list
- **Default sort**: entries by `created_at DESC`
- **Entry count on book fetch**: computed via query-time COUNT, not stored
- **Auth**: JWT access + refresh tokens, email+password, email verification required, no social login

## Backlog / Not in v1

- Share entry / share link feature
- Book sharing / multi-user collaboration
