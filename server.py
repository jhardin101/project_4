from flask import Flask, jsonify, request
import sqlite3
from contextlib import closing

DATABASE_PATH = "games.db"

server = Flask(__name__)


# Games Table
CREATE_TABLE_SQL = """
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
"""

REQUIRED_FIELDS = [
        "title", "platform", "genre", "release_year", "status"
    ]

STRING_FIELDS = {"title", "platform", "genre", "status"}

ALLOWED_STATUSES = {"Backlog", "Playing", "Completed"}

class GameDatabase:
    def __init__(self, database_path=DATABASE_PATH):
        self.database_path = database_path
        self.initialize()

    def initialize(self):
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.execute(CREATE_TABLE_SQL)

    def get_all_games(self):
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute("SELECT * FROM games ORDER BY id").fetchall()

            return [dict(row) for row in rows]

    def get_game(self, game_id):
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT * FROM games WHERE id = ?", (game_id,)
            ).fetchone()

            return dict(row) if row is not None else None

    # Database POST
    def create_game(self, game):
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    INSERT INTO games (title, platform, genre, release_year, status, rating, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        game["title"],
                        game["platform"],
                        game["genre"],
                        game["release_year"],
                        game["status"],
                        game.get("rating"),
                        game.get("notes"),
                    ),
                )
            return cursor.lastrowid

    # Database PUT
    def replace_game(self, game_id, game):
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    UPDATE games
                    SET title = ?, platform = ?, genre = ?, release_year = ?,
                        status = ?, rating = ?, notes = ?
                    WHERE id = ?
                    """,
                    (
                        game["title"],
                        game["platform"],
                        game["genre"],
                        game["release_year"],
                        game["status"],
                        game.get("rating"),
                        game.get("notes"),
                        game_id,
                    ),
                )
            return cursor.rowcount > 0

    # Database DELETE
    def delete_game(self, game_id):
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                cursor = connection.execute(
                    "DELETE FROM games WHERE id = ?", (game_id,)
                )
            return cursor.rowcount > 0

database = GameDatabase()
# GET Routes
@server.route("/api/games", methods=["GET"])
def list_games():
    return jsonify(database.get_all_games())

@server.route("/api/games/<int:game_id>", methods=["GET"])
def get_game(game_id):
    game = database.get_game(game_id)

    if game is None:
        return jsonify({"error": "Game not found"}), 404

    return jsonify(game), 200

# POST route
@server.route("/api/games", methods=["POST"])
def create_game():
    game = request.get_json(silent=True)

    if not isinstance(game, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    # Field checks

    required_fields = REQUIRED_FIELDS

    missing_fields = [field for field in required_fields if field not in game or game[field] == ""]
    if missing_fields:
        return jsonify({
            "error":"Missing required fields",
            "fields": missing_fields
        }), 400

    for field in ("title", "platform", "genre", "status"):
        if not isinstance(game[field], str) or not game[field].strip():
            return jsonify({"error": f"{field} must be a non-empty string"}), 400
        game[field] = game[field].strip()

    year = game["release_year"]
    if isinstance(year, bool) or not isinstance(year, int) or year < 1958:
        return jsonify({"error":"release_year must be an integer of 1958 or later"}), 400

    allowed_statuses = {"Backlog", "Playing", "Completed"}
    if game["status"] not in allowed_statuses:
        return jsonify({"error": "status must be Backlog, Playing, or Completed"}), 400

    rating = game.get("rating")
    if rating is not None and (isinstance(rating, bool) or not isinstance(rating, int) or not 1 <= rating <= 5):
        return jsonify({"error":"rating must be an integer from 1 to 5, or null"}), 400

    notes = game.get("notes")
    if notes is not None and not isinstance(notes, str):
        return jsonify({"error":"notes must be text or null"}), 400

    game_id = database.create_game(game)
    created_game = database.get_game(game_id)

    response = jsonify(created_game)
    response.status_code = 201
    response.headers["Location"] = f"/api/games/{game_id}"
    return response

# PUT route
@server.route("/api/games/<int:game_id>", methods=["PUT"])
def replace_game(game_id):
    # Return 404 if game with this id not found
    if database.get_game(game_id) is None:
        return jsonify({"error":"Game not found"}), 404

    game = request.get_json(silent=True)
    if not isinstance(game, dict):
        return jsonify({"error":"Request body must be a JSON object"}), 400

    required_fields = REQUIRED_FIELDS

    missing_fields = [field for field in required_fields if field not in game or game[field] == ""]

    if missing_fields:
        return jsonify({"error":"Missing required fields", "fields":missing_fields}), 400

    for field in (STRING_FIELDS):
        if not isinstance(game[field], str) or not game[field].strip():
            return jsonify({"error":f"{field} must be a non-empty string"}), 400

        game[field] = game[field].strip()

    year = game["release_year"]
    if isinstance(year, bool) or not isinstance(year, int) or year < 1958:
        return jsonify({"error":"release_year must be an integer of 1958 or later"}), 400

    allowed_statuses = ALLOWED_STATUSES
    if game["status"] not in allowed_statuses:
        return jsonify({"error":"status must be Backlog, Playing, or Completed"}), 400

    rating = game.get("rating")
    if rating is not None and (isinstance(rating, bool) or not isinstance(rating, int) or not 1 <= rating <= 5):
        return jsonify({"error":"rating must be an integer from 1 to 5 or null"}), 400

    notes = game.get("notes")
    if notes is not None and not isinstance(notes, str):
        return jsonify({"error":"notes must be text or null"}), 400

    database.replace_game(game_id, game)
    updated_game = database.get_game(game_id)
    return jsonify(updated_game), 200

# DELETE route
@server.route("/api/games/<int:game_id>", methods=["DELETE"])
def delete_game(game_id):
    if not database.delete_game(game_id):
        return jsonify({"error":"Game not found"}), 404

    return "", 204

@server.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = ("GET, POST, PUT, DELETE, OPTIONS")
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response
