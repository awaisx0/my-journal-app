from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings

from routers.auth import router as auth_router
from routers.journal_books import router as journal_books_router
from routers.journal_entries import router as journal_entries_router

app = FastAPI()

# The browser frontend is served from a different origin (Vite's dev
# server) than this API, so every request from it is cross-origin.
# allow_credentials is required for the httpOnly refresh cookie that
# /auth/refresh reads to be sent at all.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(journal_books_router, prefix="/journal_books", tags=["journalbooks"])
# No prefix here: each entries route already spells out its own full path
# ("/{book_id}/entries" for the nested list/create, "/entries/{id}" for
# direct lookups), since it needs both URL shapes at once.
app.include_router(journal_entries_router, tags=["entries"])


