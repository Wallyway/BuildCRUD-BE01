# Task API

A small CRUD API for managing a to-do list, built with FastAPI and backed by PostgreSQL running in Docker.

## Run the whole stack

```
cp .env.example .env
docker compose up
```

That single command builds the app image, starts PostgreSQL with a volume, waits until the database reports healthy, and then starts the API.

Server runs at http://localhost:8000. Interactive docs at http://localhost:8000/docs.

## Run without Docker

The storage backend is chosen by an environment variable, so the API also runs against SQLite with no database server at all:

```
pip install -r requirements.txt
DB_BACKEND=sqlite uvicorn main:app --reload --port 8000
```

To run the app locally against the Postgres container, start only the database with `docker compose up db` and set `DATABASE_URL` to use `localhost` instead of `db`.

## Configuration

Settings come from `.env`, which is gitignored. `.env.example` is committed with the same keys:

| Variable | Purpose |
|-------------------|--------------------------------------------------|
| DB_BACKEND        | `postgres` or `sqlite`                           |
| DATABASE_URL      | Postgres connection string                       |
| SQLITE_PATH       | Database file used by the sqlite backend         |
| POSTGRES_USER     | Credentials the database container is created with |
| POSTGRES_PASSWORD | Credentials the database container is created with |
| POSTGRES_DB       | Credentials the database container is created with |

Inside Compose the host is `db`, the service name on the Compose network. Outside Docker it is `localhost`.

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

## Where the data lives

PostgreSQL stores its data in the named volume `pgdata`, mounted at `/var/lib/postgresql/data`. The volume is what survives, not the containers: `docker compose down` removes the containers and the data stays, while `docker compose down -v` deletes the volume and wipes everything.

The table is created by a single SQL file, [db/init.sql](db/init.sql), mounted into `/docker-entrypoint-initdb.d/`. Postgres only runs that directory when the volume is empty, so the schema and the three example tasks are created on the very first start and never again.

## Persistence check

Run against the stack started with `docker compose up`:

```
$ curl -s -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Sobrevive al reinicio"}'
{"id":5,"title":"Sobrevive al reinicio","done":false}

$ docker compose down
 Container buildcrud-be01-app-1  Removed
 Container buildcrud-be01-db-1   Removed
 Network buildcrud-be01_default  Removed

$ docker compose up -d
 Container buildcrud-be01-db-1   Healthy
 Container buildcrud-be01-app-1  Started

$ curl -s http://localhost:8000/tasks
[{"id":1,"title":"Buy groceries","done":false},{"id":2,"title":"Write report","done":false},{"id":3,"title":"Walk the dog","done":true},{"id":5,"title":"Sobrevive al reinicio","done":false}]
```

Task 5 is still there after both containers were destroyed and rebuilt, and the seed tasks were not inserted a second time. Deleting the volume instead reverses it:

```
$ docker compose down -v && docker compose up -d
$ curl -s http://localhost:8000/tasks
[{"id":1,"title":"Buy groceries","done":false},{"id":2,"title":"Write report","done":false},{"id":3,"title":"Walk the dog","done":true}]
```

Only the three seeds come back, which confirms the volume was holding the data.

![Postgres in Docker](docs/postgres.png)

## Architecture, honestly

The assignment assumes the previous version already had a repository behind an interface, so that swapping storage would touch one file. That was not true here: the previous version was a single `main.py` with SQLite queries written inside every route handler. The layers were extracted first, in stages 0 to 2 of this assignment:

| File | Role |
|--------------------|-------------------------------------------------|
| `repository.py`    | `TaskRepository` protocol, the interface         |
| `repo_sqlite.py`   | SQLite implementation                            |
| `repo_postgres.py` | PostgreSQL implementation                        |
| `service.py`       | Validation rules, 400 and 404 decisions          |
| `routes.py`        | HTTP endpoints, delegating to the service        |
| `main.py`          | Wiring: picks a repository and builds the app    |

With that in place, the claim holds and the git history proves it. Adding PostgreSQL touched neither the service nor the routes:

```
$ git show --stat ":/Stage 6: postgres repository"
 repo_postgres.py | 34 ++++++++++++++++++++++++++++++++++
 requirements.txt |  1 +
 2 files changed, 35 insertions(+)

$ git show --stat ":/Stage 7: select repository"
 .env.example |  2 +-
 main.py      | 12 ++++++++++--
 2 files changed, 11 insertions(+), 3 deletions(-)
```

`service.py` and `routes.py` appear in neither commit. The same 16 request-and-response checks — status codes, bodies, and error messages — pass identically against SQLite and against PostgreSQL.

## SQLite notes

The SQLite backend from the previous assignment is still available through `DB_BACKEND=sqlite`, which is what makes the swap demonstrable rather than merely claimed.

![DB Browser for SQLite](docs/database.png)

```
sqlite> SELECT * FROM tasks WHERE done = 1;
3|Walk the dog|1
```

More queries in [docs/queries.sql](docs/queries.sql).
