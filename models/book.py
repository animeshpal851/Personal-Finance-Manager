"""
Book model and Singly Linked List node definition for Library Management.
"""

from datetime import datetime


class Book:
    """Represents a single book record stored in a linked list node."""

    def __init__(self, book_id: str, title: str, author: str, genre: str = ""):
        self.book_id = book_id.strip()
        self.title = title.strip()
        self.author = author.strip()
        self.genre = genre.strip()
        self.added_at = datetime.now()

    def to_dict(self) -> dict:
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "added_at": self.added_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        book = cls(
            book_id=data.get("book_id", ""),
            title=data.get("title", ""),
            author=data.get("author", ""),
            genre=data.get("genre", ""),
        )
        book.added_at = data.get("added_at", datetime.now())
        return book


class LinkedListNode:
    """A node in the singly linked list, wrapping a Book object."""

    def __init__(self, book: Book):
        self.book: Book = book
        self.next: "LinkedListNode | None" = None
