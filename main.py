from fastapi import FastAPI

from routers.auth import router as auth_router
from routers.journal_books import router as journal_books_router
from routers.journal_entries import router as journal_entries_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(journal_books_router, prefix="/journal_books", tags=["journalbooks"])
# No prefix here: each entries route already spells out its own full path
# ("/{book_id}/entries" for the nested list/create, "/entries/{id}" for
# direct lookups), since it needs both URL shapes at once.
app.include_router(journal_entries_router, tags=["entries"])


