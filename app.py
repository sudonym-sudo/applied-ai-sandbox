"""Tiny Flask app — applied-ai-sandbox.

Each task in tasks/ asks you to add or fix one piece. The tests in tests/
describe exactly what "done" means.
"""
from __future__ import annotations

import time

from flask import Flask, render_template, request, redirect, url_for


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "sandbox-not-a-real-secret"

    # In-memory store for the sandbox. Resets on every restart, which is
    # fine for practice. Real apps use a database.
    class NotesList(list):
        """Small list subclass that ensures every note dict has a `tags` key.

        This keeps the in-memory shape (plain dicts) while allowing callers
        to append directly (tests sometimes do) and still get a default
        `tags` field.
        """

        @staticmethod
        def _ensure(note: dict) -> dict:
            if isinstance(note, dict):
                note.setdefault("tags", [])
                note.setdefault("is_pinned", False)
                note.setdefault("updated_at", time.time())
            return note

        def append(self, note):
            super().append(self._ensure(note))

        def extend(self, iterable):
            super().extend(self._ensure(item) for item in iterable)

        def insert(self, index, note):
            super().insert(index, self._ensure(note))

        def __setitem__(self, index, value):
            # support slice and single-index assignment
            if isinstance(index, slice):
                value = [self._ensure(v) for v in value]
            else:
                value = self._ensure(value)
            super().__setitem__(index, value)

    app.notes: NotesList = NotesList()  # type: ignore[attr-defined]

    @app.route("/")
    def home():
        sorted_notes = sorted(
            app.notes,
            key=lambda note: (
                not note.get("is_pinned", False),
                -note.get("updated_at", 0),
            ),
        )
        return render_template("home.html", notes=sorted_notes)

    @app.route("/notes/<int:idx>/pin", methods=["POST"])
    def toggle_pin(idx):
        if idx < 0 or idx >= len(app.notes):
            return "Not found", 404

        note = app.notes[idx]
        note.setdefault("is_pinned", False)
        note.setdefault("updated_at", time.time())

        desired = request.form.get("is_pinned")
        if desired is None:
            note["is_pinned"] = not note["is_pinned"]
        else:
            note["is_pinned"] = str(desired).lower() in ("1", "true", "yes", "on")

        note["updated_at"] = time.time()
        return redirect(url_for("home"))

    @app.route("/notes/new", methods=["GET", "POST"])
    def new_note():
        if request.method == "POST":
            title = (request.form.get("title") or "").strip()
            body = (request.form.get("body") or "").strip()
            error = None

            if not title:
                error = "Title is required"
            elif not body:
                error = "Body is required"

            if error:
                return render_template(
                    "new_note.html",
                    title=title,
                    body=body,
                    error=error,
                )

            app.notes.append(
                {
                    "title": title,
                    "body": body,
                    "is_pinned": False,
                    "updated_at": time.time(),
                }
            )
            return redirect(url_for("home"))
        return render_template("new_note.html")

    # TASK 02 will add a /notes/<idx>/delete route here.

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
