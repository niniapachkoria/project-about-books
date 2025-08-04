from flask import Flask, jsonify, request
import os
import json

app = Flask(__name__)

DATA_FILE = "books.json"


def load_books():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_books(books):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=4)


@app.route("/")
def home():
    return """
    <h1>📚 წიგნების მაღაზია</h1>
    <p>ეს საიტი გაძლევთ საშუალებას დაამატოთ, წაშალოთ, ნახოთ და რედაქტიროთ წიგნები JSON ფაილში.</p>
    """


@app.route("/books", methods=["GET"])
def all_books():
    books = load_books()
    if not books:
        return jsonify({"message": "წიგნები არ მოიძებნა."}), 404
    return jsonify(books)


@app.route("/details/<int:book_id>", methods=["GET"])
def detailed_book(book_id):
    books = load_books()
    for book in books:
        if book["id"] == book_id:
            return jsonify(book)
    return jsonify({"error": "წიგნი ვერ მოიძებნა."}), 404


@app.route("/add_book", methods=["POST"])
def add_book():
    data = request.get_json()
    books = load_books()

    if not data.get("title") or not data.get("author"):
        return jsonify({"error": "სათაური და ავტორი აუცილებელია"}), 400

    new_id = max([book["id"] for book in books], default=0) + 1
    new_book = {
        "id": new_id,
        "title": data.get("title"),
        "author": data.get("author"),
        "rate": data.get("rate", 0),
        "status": data.get("status", "კითხვის პროცესში")
    }
    books.append(new_book)
    save_books(books)

    return jsonify({
        "book": new_book,
        "message": "წიგნი წარმატებით დაემატა!"
    }), 201


@app.route("/edit_book/<int:book_id>", methods=["PUT"])
def edit_book(book_id):
    books = load_books()
    data = request.get_json()

    for book in books:
        if book["id"] == book_id:
            book["title"] = data.get("title", book["title"])
            book["author"] = data.get("author", book["author"])
            book["rate"] = data.get("rate", book.get("rate", 0))
            book["status"] = data.get("status", book.get("status", "კითხვის პროცესში"))

            save_books(books)
            return jsonify({
                "book": book,
                "message": "წიგნი წარმატებით დარედაქტირდა!"
            }), 200

    return jsonify({"error": "წიგნი ვერ მოიძებნა."}), 404


@app.route("/delete/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    books = load_books()
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            save_books(books)
            return jsonify({"message": "წიგნი წარმატებით წაიშალა."}), 200
    return jsonify({"error": "წიგნი ვერ მოიძებნა."}), 404


if __name__ == "__main__":
    app.run(debug=True)

