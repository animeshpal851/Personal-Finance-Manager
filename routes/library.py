"""
Library Management routes — Singly Linked List visualization.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from services.library_service import LibraryService

library_bp = Blueprint("library", __name__)


def _svc() -> LibraryService:
    """Fresh service instance per request (reloads list from MongoDB)."""
    return LibraryService()


# ── Page routes ────────────────────────────────────────────────────────────────

@library_bp.route("/library")
def index():
    svc = _svc()
    books = svc.get_all_books()
    viz = svc.get_visualization_data()
    return render_template(
        "library.html",
        books=books,
        viz=viz,
        total=svc.count,
        search_query="",
        search_results=None,
        search_steps=[],
    )


@library_bp.route("/library/add", methods=["POST"])
def add():
    book_id = request.form.get("book_id", "").strip()
    title   = request.form.get("title", "").strip()
    author  = request.form.get("author", "").strip()
    genre   = request.form.get("genre", "").strip()

    svc = _svc()
    result = svc.add_book(book_id, title, author, genre)
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("library.index"))


@library_bp.route("/library/delete/<book_id>", methods=["POST"])
def delete(book_id: str):
    svc = _svc()
    result = svc.delete_book(book_id)
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("library.index"))


@library_bp.route("/library/update/<book_id>", methods=["POST"])
def update(book_id: str):
    title  = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    genre  = request.form.get("genre", "").strip()

    svc = _svc()
    result = svc.update_book(book_id, title, author, genre)
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("library.index"))


@library_bp.route("/library/search")
def search():
    query = request.args.get("q", "").strip()
    svc = _svc()

    if query:
        result = svc.search_books(query)
        flash(result["message"], "info")
        books = svc.get_all_books()
        viz = svc.get_visualization_data()
        return render_template(
            "library.html",
            books=books,
            viz=viz,
            total=svc.count,
            search_query=query,
            search_results=result["results"],
            search_steps=result["steps"],
        )

    return redirect(url_for("library.index"))


# ── JSON API ───────────────────────────────────────────────────────────────────

@library_bp.route("/api/library/books")
def api_books():
    """Return the full linked list structure as JSON for visualization."""
    svc = _svc()
    return jsonify(svc.get_visualization_data())


@library_bp.route("/api/library/search")
def api_search():
    """Return search results with traversal steps for animation."""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"results": [], "steps": [], "message": "No query provided."})

    svc = _svc()
    result = svc.search_books(query)
    return jsonify(result)


@library_bp.route("/api/library/delete/<book_id>", methods=["POST"])
def api_delete(book_id: str):
    """Delete a book and return traversal steps for animation."""
    svc = _svc()
    result = svc.delete_book(book_id)
    return jsonify(result)
