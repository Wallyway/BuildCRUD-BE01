from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import sqlite3

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A small CRUD API for managing tasks, stored in SQLite.",
)

DB_PATH = "tasks.db"

db = sqlite3.connect(DB_PATH, check_same_thread=False)
db.row_factory = sqlite3.Row


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


def init_db():
    db.execute(
        "CREATE TABLE IF NOT EXISTS tasks ("
        "id INTEGER PRIMARY KEY, "
        "title TEXT NOT NULL, "
        "done INTEGER NOT NULL DEFAULT 0)"
    )
    count = db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if count == 0:
        db.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [("Buy groceries", 0), ("Write report", 0), ("Walk the dog", 1)],
        )
    db.commit()


def row_to_task(row):
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


init_db()


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
    rows = db.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()
    return [row_to_task(row) for row in rows]


@app.get("/tasks/{task_id}", tags=["tasks"], summary="Get a task", description="Returns a single task by id, or 404 if it does not exist.")
def get_task(task_id: int):
    row = db.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return row_to_task(row)


@app.post("/tasks", status_code=201, tags=["tasks"], summary="Create a task", description="Creates a task from a title. Rejects a missing or empty title with 400.")
def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="title is required")
    cursor = db.execute("INSERT INTO tasks (title, done) VALUES (?, 0)", (task.title,))
    db.commit()
    return {"id": cursor.lastrowid, "title": task.title, "done": False}


@app.put("/tasks/{task_id}", tags=["tasks"], summary="Update a task", description="Replaces title and/or done for a task. 404 unknown id, 400 empty or invalid body.")
def update_task(task_id: int, update: TaskUpdate):
    row = db.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    if update.title is None and update.done is None:
        raise HTTPException(status_code=400, detail="title and/or done is required")
    title = row["title"]
    if update.title is not None:
        if not update.title.strip():
            raise HTTPException(status_code=400, detail="title cannot be empty")
        title = update.title
    done = row["done"] if update.done is None else update.done
    db.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (title, int(done), task_id))
    db.commit()
    return {"id": task_id, "title": title, "done": bool(done)}


@app.delete("/tasks/{task_id}", status_code=204, tags=["tasks"], summary="Delete a task", description="Removes a task. 404 if the id does not exist.")
def delete_task(task_id: int):
    cursor = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    db.commit()
