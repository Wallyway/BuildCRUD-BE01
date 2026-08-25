# Task API

A small in-memory CRUD API for managing a to-do list, built with FastAPI.

## Install & run

```
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Server runs at http://localhost:8000. Interactive docs at http://localhost:8000/docs.

## Endpoints

| Method | Path         | Description                          |
|--------|--------------|---------------------------------------|
| GET    | /            | API info                              |
| GET    | /health      | Health check                          |
| GET    | /tasks       | List all tasks                        |
| GET    | /tasks/{id}  | Get a single task                     |
| POST   | /tasks       | Create a task                         |
| PUT    | /tasks/{id}  | Update a task's title and/or done     |
| DELETE | /tasks/{id}  | Delete a task                         |

## Example

```
$ curl -i -X PUT http://localhost:8000/tasks/4 -H "Content-Type: application/json" -d '{"done":true}'
HTTP/1.1 200 OK
content-type: application/json

{"id":4,"title":"Buy milk","done":true}
```

## Swagger UI

![Swagger UI](docs/swagger.png)

## Data persistence

Tasks live only in memory. Restarting the server resets the list back to the three seed tasks — anything created, updated, or deleted during a session is lost. This is expected: without a database, the process has nowhere else to keep the data.
