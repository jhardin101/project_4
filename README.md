# Game Library

A web application for keeping track of video games. The client uses a Flask API to create, view, update, and delete game records stored in SQLite.

## Resource and attributes

The resource is **Game**. Each game has:

| Attribute | Description |
|---|---|
| `id` | Unique integer identifier, assigned by SQLite |
| `title` | Game title |
| `platform` | Platform the game is played on |
| `genre` | Game genre |
| `release_year` | Release year; must be 1958 or later |
| `status` | `Backlog`, `Playing`, or `Completed` |
| `rating` | Optional integer from 1 to 5 |
| `notes` | Optional notes |

## Database schema

```sql
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    platform TEXT NOT NULL,
    genre TEXT NOT NULL,
    release_year INTEGER NOT NULL CHECK (release_year >= 1958),
    status TEXT NOT NULL CHECK (status IN ('Backlog', 'Playing', 'Completed')),
    rating INTEGER CHECK (rating IS NULL OR rating BETWEEN 1 AND 5),
    notes TEXT
);
```

## REST API

The API base path is `/api/games`.

| Action | Method | Path | Successful response |
|---|---|---|---|
| List games | `GET` | `/api/games` | `200 OK` with a JSON array |
| Retrieve a game | `GET` | `/api/games/{id}` | `200 OK` with a JSON object |
| Create a game | `POST` | `/api/games` | `201 Created` with the new game |
| Replace a game | `PUT` | `/api/games/{id}` | `200 OK` with the updated game |
| Delete a game | `DELETE` | `/api/games/{id}` | `204 No Content` |
| Automatically handled by Flask | `OPTIONS` | `/api/games/{id}, /api/games` | CORS headers |

Requests that refer to a game ID that does not exist return `404 Not Found`. Invalid JSON or game data returns `400 Bad Request`.

The server adds CORS headers to responses. Flask automatically handles `OPTIONS` for registered routes, which allows browsers to make preflight requests.

## Running the server

From the project directory, run:

```powershell
flask --app server run
```

The API will be available at `http://127.0.0.1:5000`. The SQLite database file, `games.db`, is created in the working directory when the server initializes.