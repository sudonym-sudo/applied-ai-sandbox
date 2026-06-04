"""Acceptance tests for TASK 03 — pin notes and sort pinned items first."""


def _seed(app, notes):
    app.notes.clear()
    for note in notes:
        app.notes.append(note)


def test_toggle_pin_updates_note_state_and_redirects(client, app):
    _seed(app, [{"title": "Note 1", "body": "Body 1"}])

    response = client.post("/notes/0/pin", data={"is_pinned": "1"})

    assert response.status_code in (302, 303)
    assert app.notes[0]["is_pinned"] is True


def test_homepage_sorts_pinned_notes_first(client, app):
    _seed(app, [
        {"title": "Old unpinned", "body": "A", "updated_at": 1, "is_pinned": False},
        {"title": "New unpinned", "body": "B", "updated_at": 2, "is_pinned": False},
        {"title": "Pinned older", "body": "C", "updated_at": 1.5, "is_pinned": True},
        {"title": "Pinned newer", "body": "D", "updated_at": 3, "is_pinned": True},
    ])

    response = client.get("/")
    body = response.data.decode()

    assert body.index("Pinned newer") < body.index("Pinned older")
    assert body.index("Pinned older") < body.index("New unpinned")


def test_pin_route_returns_404_for_missing_note(client, app):
    app.notes.clear()
    response = client.post("/notes/99/pin", data={"is_pinned": "1"})
    assert response.status_code == 404
