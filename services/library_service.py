"""
Library Service — Singly Linked List implementation for Library Management.

The SinglyLinkedList class implements the data structure manually.
The LibraryService class uses the linked list as the primary in-memory data
structure and syncs operations to MongoDB for persistence.
"""

import logging
from datetime import datetime
from typing import List, Optional

from database.mongo_connection import connection
from models.book import Book, LinkedListNode

logger = logging.getLogger(__name__)

LIBRARY_COLLECTION = "library_books"


# ── Singly Linked List ─────────────────────────────────────────────────────────

class SinglyLinkedList:
    """
    A manually implemented singly linked list where each node holds a Book.

    Supported operations:
        insert_at_end(book)       – append a new node
        insert_at_beginning(book) – prepend a new node
        delete_by_id(book_id)     – remove node by Book ID, returns traversal steps
        search(query)             – find books matching ID or title substring,
                                    returns (results, traversal_steps)
        update(book_id, **fields) – modify a book's attributes in-place
        to_list()                 – return all books as a plain list
        __len__()                 – number of nodes
    """

    def __init__(self):
        self.head: Optional[LinkedListNode] = None
        self._size: int = 0

    # ── Insertion ────────────────────────────────────────────────────────────

    def insert_at_end(self, book: Book) -> None:
        """Append a new node to the tail of the list — O(n)."""
        node = LinkedListNode(book)
        if self.head is None:
            self.head = node
        else:
            current = self.head
            while current.next is not None:
                current = current.next
            current.next = node
        self._size += 1

    def insert_at_beginning(self, book: Book) -> None:
        """Prepend a new node to the head of the list — O(1)."""
        node = LinkedListNode(book)
        node.next = self.head
        self.head = node
        self._size += 1

    # ── Deletion ─────────────────────────────────────────────────────────────

    def delete_by_id(self, book_id: str) -> dict:
        """
        Remove the first node whose book_id matches.

        Returns a dict with:
          - 'success': bool
          - 'steps': list of traversal step dicts (for animation)
          - 'deleted_book': Book dict or None
        """
        steps = []
        if self.head is None:
            return {"success": False, "steps": steps, "deleted_book": None}

        book_id = book_id.strip()

        # Special case: head node is the target
        if self.head.book.book_id == book_id:
            steps.append({
                "node_id": self.head.book.book_id,
                "action": "found",
                "position": 0,
            })
            deleted = self.head.book.to_dict()
            self.head = self.head.next
            self._size -= 1
            return {"success": True, "steps": steps, "deleted_book": deleted}

        prev = self.head
        current = self.head
        position = 0

        while current is not None:
            steps.append({
                "node_id": current.book.book_id,
                "action": "found" if current.book.book_id == book_id else "visit",
                "position": position,
            })
            if current.book.book_id == book_id:
                prev.next = current.next
                self._size -= 1
                return {
                    "success": True,
                    "steps": steps,
                    "deleted_book": current.book.to_dict(),
                }
            prev = current
            current = current.next
            position += 1

        return {"success": False, "steps": steps, "deleted_book": None}

    # ── Search ────────────────────────────────────────────────────────────────

    def search(self, query: str) -> dict:
        """
        Traverse the list and return all books where book_id, title, or author
        contains `query` (case-insensitive).

        Returns a dict with:
          - 'results': list of matching Book dicts
          - 'steps': list of traversal step dicts (for animation)
        """
        query_lower = query.strip().lower()
        results = []
        steps = []
        current = self.head
        position = 0

        while current is not None:
            book = current.book
            matched = (
                query_lower in book.book_id.lower()
                or query_lower in book.title.lower()
                or query_lower in book.author.lower()
                or query_lower in book.genre.lower()
            )
            steps.append({
                "node_id": book.book_id,
                "action": "found" if matched else "visit",
                "position": position,
            })
            if matched:
                results.append(book.to_dict())
            current = current.next
            position += 1

        return {"results": results, "steps": steps}

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, book_id: str, title: str, author: str, genre: str) -> Optional[Book]:
        """
        Update a book's fields by book_id.  Returns the updated Book or None.
        Traverses the list linearly — O(n).
        """
        current = self.head
        while current is not None:
            if current.book.book_id == book_id.strip():
                current.book.title = title.strip()
                current.book.author = author.strip()
                current.book.genre = genre.strip()
                return current.book
            current = current.next
        return None

    # ── Utilities ─────────────────────────────────────────────────────────────

    def to_list(self) -> List[dict]:
        """Return an ordered list of all book dicts (head → tail)."""
        result = []
        current = self.head
        while current is not None:
            result.append(current.book.to_dict())
            current = current.next
        return result

    def find_by_id(self, book_id: str) -> Optional[Book]:
        current = self.head
        while current is not None:
            if current.book.book_id == book_id.strip():
                return current.book
            current = current.next
        return None

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._size > 0


# ── Library Service ────────────────────────────────────────────────────────────

class LibraryService:
    """
    Facade over SinglyLinkedList + MongoDB.

    The linked list is the canonical in-memory structure for all operations.
    MongoDB provides persistence so data survives restarts.
    """

    def __init__(self):
        self._ll = SinglyLinkedList()
        self._col = connection.get_collection(LIBRARY_COLLECTION)
        self._load_from_db()

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _load_from_db(self) -> None:
        """Rebuild the in-memory linked list from MongoDB (ordered by added_at)."""
        self._ll = SinglyLinkedList()
        for doc in self._col.find({}, {"_id": 0}).sort("added_at", 1):
            book = Book.from_dict(doc)
            self._ll.insert_at_end(book)

    def _id_exists(self, book_id: str) -> bool:
        return self._ll.find_by_id(book_id) is not None

    # ── CRUD operations ──────────────────────────────────────────────────────

    def add_book(self, book_id: str, title: str, author: str, genre: str = "") -> dict:
        """
        Insert a new book at the tail of the linked list and persist it.
        Returns {'success': bool, 'message': str, 'book': dict|None}.
        """
        if not book_id or not title or not author:
            return {"success": False, "message": "Book ID, title and author are required.", "book": None}

        if self._id_exists(book_id):
            return {"success": False, "message": f"Book ID '{book_id}' already exists.", "book": None}

        book = Book(book_id=book_id, title=title, author=author, genre=genre)
        self._ll.insert_at_end(book)

        try:
            self._col.insert_one(book.to_dict())
        except Exception as exc:
            logger.error("DB insert failed: %s", exc)
            # Roll back in-memory change
            self._load_from_db()
            return {"success": False, "message": "Database error — book not saved.", "book": None}

        return {"success": True, "message": f"Book '{title}' added successfully.", "book": book.to_dict()}

    def delete_book(self, book_id: str) -> dict:
        """
        Remove a book by ID. Returns traversal steps for animation.
        """
        result = self._ll.delete_by_id(book_id)
        if result["success"]:
            try:
                self._col.delete_one({"book_id": book_id.strip()})
            except Exception as exc:
                logger.error("DB delete failed: %s", exc)
                self._load_from_db()
                return {"success": False, "message": "Database error — book not deleted.", "steps": []}

        return {
            "success": result["success"],
            "message": f"Book '{book_id}' deleted." if result["success"] else f"Book '{book_id}' not found.",
            "steps": result["steps"],
            "deleted_book": result["deleted_book"],
        }

    def search_books(self, query: str) -> dict:
        """
        Search books by ID, title, author, or genre (case-insensitive substring).
        Returns results and traversal steps for animation.
        """
        if not query or not query.strip():
            return {"results": [], "steps": [], "message": "Please enter a search query."}

        result = self._ll.search(query)
        count = len(result["results"])
        msg = f"Found {count} book(s) matching '{query}'." if count else f"No books found matching '{query}'."
        return {
            "results": result["results"],
            "steps": result["steps"],
            "message": msg,
        }

    def update_book(self, book_id: str, title: str, author: str, genre: str) -> dict:
        """Update an existing book's details."""
        if not title or not author:
            return {"success": False, "message": "Title and author are required."}

        updated = self._ll.update(book_id, title, author, genre)
        if updated is None:
            return {"success": False, "message": f"Book '{book_id}' not found."}

        try:
            self._col.update_one(
                {"book_id": book_id.strip()},
                {"$set": {"title": updated.title, "author": updated.author, "genre": updated.genre}},
            )
        except Exception as exc:
            logger.error("DB update failed: %s", exc)
            self._load_from_db()
            return {"success": False, "message": "Database error — book not updated."}

        return {"success": True, "message": f"Book '{book_id}' updated successfully.", "book": updated.to_dict()}

    def get_all_books(self) -> List[dict]:
        """Return all books in linked list order (head → tail)."""
        return self._ll.to_list()

    def get_book(self, book_id: str) -> Optional[dict]:
        book = self._ll.find_by_id(book_id)
        return book.to_dict() if book else None

    # ── Visualization data ────────────────────────────────────────────────────

    def get_visualization_data(self) -> dict:
        """
        Return the full linked list structure for frontend rendering.

        Each entry contains:
          - book_id, title, author, genre
          - has_next: bool (False for the last node)
          - position: int (0-based index)
        """
        nodes = []
        current = self._ll.head
        position = 0
        while current is not None:
            b = current.book
            nodes.append({
                "book_id": b.book_id,
                "title": b.title,
                "author": b.author,
                "genre": b.genre,
                "has_next": current.next is not None,
                "position": position,
            })
            current = current.next
            position += 1

        return {
            "nodes": nodes,
            "total": len(nodes),
            "has_head": self._ll.head is not None,
        }

    @property
    def count(self) -> int:
        return len(self._ll)
