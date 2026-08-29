from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from repo_sqlite import SqliteTaskRepository
from service import TaskService

DB_PATH = "tasks.db"

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A small CRUD API for managing tasks, stored in SQLite.",
)

service = TaskService(SqliteTaskRepository(DB_PATH))


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Invalid request body"})


@app.get("/", summary="API info", description="Describes this API and its main endpoints.")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check", description="Reports whether the server is running.")
def health():
    return {"status": "ok"}


@app.get("/tasks", tags=["tasks"], summary="List tasks", description="Returns every task.")
def list_tasks():
    return service.list_tasks()


@app.get("/tasks/{task_id}", tags=["tasks"], summary="Get a task", description="Returns a single task by id, or 404 if it does not exist.")
def get_task(task_id: int):
    return service.get_task(task_id)


@app.post("/tasks", status_code=201, tags=["tasks"], summary="Create a task", description="Creates a task from a title. Rejects a missing or empty title with 400.")
def create_task(task: TaskCreate):
    return service.create_task(task.title)


@app.put("/tasks/{task_id}", tags=["tasks"], summary="Update a task", description="Replaces title and/or done for a task. 404 unknown id, 400 empty or invalid body.")
def update_task(task_id: int, update: TaskUpdate):
    return service.update_task(task_id, update.title, update.done)


@app.delete("/tasks/{task_id}", status_code=204, tags=["tasks"], summary="Delete a task", description="Removes a task. 404 if the id does not exist.")
def delete_task(task_id: int):
    service.delete_task(task_id)
