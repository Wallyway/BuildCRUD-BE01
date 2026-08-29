from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import config
from repo_sqlite import SqliteTaskRepository
from routes import router
from service import TaskService

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A small CRUD API for managing tasks, stored in SQLite.",
)

app.state.service = TaskService(SqliteTaskRepository(config.SQLITE_PATH))


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Invalid request body"})


app.include_router(router)
