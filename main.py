from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A small in-memory CRUD API for managing tasks.",
)


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Write report", "done": False},
    {"id": 3, "title": "Walk the dog", "done": True},
]


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
    return tasks


@app.get("/tasks/{task_id}", tags=["tasks"], summary="Get a task", description="Returns a single task by id, or 404 if it does not exist.")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.post("/tasks", status_code=201, tags=["tasks"], summary="Create a task", description="Creates a task from a title. Rejects a missing or empty title with 400.")
def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="title is required")
    new_task = {
        "id": max((t["id"] for t in tasks), default=0) + 1,
        "title": task.title,
        "done": False,
    }
    tasks.append(new_task)
    return new_task


@app.put("/tasks/{task_id}", tags=["tasks"], summary="Update a task", description="Replaces title and/or done for a task. 404 unknown id, 400 empty or invalid body.")
def update_task(task_id: int, update: TaskUpdate):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    if update.title is None and update.done is None:
        raise HTTPException(status_code=400, detail="title and/or done is required")
    if update.title is not None:
        if not update.title.strip():
            raise HTTPException(status_code=400, detail="title cannot be empty")
        task["title"] = update.title
    if update.done is not None:
        task["done"] = update.done
    return task


@app.delete("/tasks/{task_id}", status_code=204, tags=["tasks"], summary="Delete a task", description="Removes a task. 404 if the id does not exist.")
def delete_task(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    tasks.remove(task)
