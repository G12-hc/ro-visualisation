import uvicorn
from fastapi import FastAPI

from app.routers import get_all_repo_data
from app.db.connection import initialize_db

# Create the FastAPI application instance
app = FastAPI()
app.include_router(get_all_repo_data.router)


if __name__ == "__main__":
    initialize_db()  # Initialize database or connections
    uvicorn.run(app, host="127.0.0.1", port=8000)