import sqlite3
from datetime import datetime
from flask import Flask, g, request, jsonify, abort

DB_PATH = "reviews.db"

app = Flask(__name__)


class SentimentClassifier:
    """
        Класс для класификации отзывов

        UPD: по хорошему, подключить сюда мелкую модельку обученную на бинарную классификацию плохое/хорошее
    """
    POSITIVE = ("хорош", "люблю", "нравится", "отлично", "супер", "класс")
    NEGATIVE = ("плохо", "ненавижу", "ужасно", "отстой", "неработает", "ошибка")

    @classmethod
    def classify(cls, text: str) -> str:
        lt = text.lower()
        if any(word in lt for word in cls.POSITIVE):
            return "positive"
        if any(word in lt for word in cls.NEGATIVE):
            return "negative"
        return "neutral"


def _init_db():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()

_init_db()


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_connection(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/reviews", methods=["POST"])
def add_review():
    if not request.is_json:
        abort(400, description="Expected JSON body")
    content = request.get_json(silent=True)
    if not content or "text" not in content:
        abort(400, description="Field 'text' is required")

    text = str(content["text"]).strip()
    sentiment = SentimentClassifier.classify(text)
    created_at = datetime.utcnow().isoformat()

    db = get_db()
    cur = db.execute(
        "INSERT INTO reviews (text, sentiment, created_at) VALUES (?, ?, ?)",
        (text, sentiment, created_at),
    )
    db.commit()
    review_id = cur.lastrowid

    return (
        jsonify({
            "id": review_id,
            "text": text,
            "sentiment": sentiment,
            "created_at": created_at,
        }),
        201,
    )


@app.route("/reviews", methods=["GET"])
def list_reviews():
    sentiment = request.args.get("sentiment")
    params = []
    query = "SELECT * FROM reviews"
    if sentiment:
        query += " WHERE sentiment = ?"
        params.append(sentiment)
    query += " ORDER BY id DESC"

    db = get_db()
    rows = db.execute(query, params).fetchall()
    data = [dict(r) for r in rows]
    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
