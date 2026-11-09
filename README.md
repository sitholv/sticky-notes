# Sticky Notes

Vusi Sithole | VS26060020556 | M06T05

Sticky Notes is a local notebook built with Django. A user can create a
note, view all notes, read a note, edit it and delete it after confirming.
Each note has a title and content. Creation and update times help the user
identify recent notes. The board starts empty; no example notes are inserted.

## Setup

Use Python 3.12 or later. Run these commands from this folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

On Windows use `.venv\Scripts\activate`. Open http://127.0.0.1:8000/.
The pinned versions were installed and checked in a Python 3.12 environment.
For runtime dependencies only, install `requirements.txt` instead.

The project package is `sticky_notes` and the installed application is
`notes`. The included migration creates the Note table in SQLite. The
database and collected `staticfiles/` folder are generated locally and
excluded from submission. App assets live in `notes/static/notes/`.
Django discovers this namespaced directory through its staticfiles app.
Instrument Sans and Instrument Serif are included locally under the SIL
Open Font License; see the font directory for licence and source details.
There is no Bootstrap or JavaScript dependency.

## Use and check

Choose New note, complete both fields, then Save note. Open a note title
to read it. Edit note changes the saved note. Delete note first opens a
confirmation page; Keep note cancels. Only a CSRF-protected POST removes
the note. Titles allow 120 characters and content allows 10,000 characters.
Whitespace-only fields are rejected, invalid forms preserve typed input,
and notes are displayed as escaped text rather than executable HTML.

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py showmigrations
python -m flake8 .
```

`design/` contains use case, sequence and class diagrams. This Part 2
version extends the Part 1 baseline with regression tests for models,
forms, routing, CRUD, invalid input, escaping and CSRF protection.

Run the isolated test database suite with `python manage.py test -v 2`.
Tests do not change the user's local notebook database.

## Scope and safety

This is a local single-user coursework application, not a private hosted
service. Notes have no user ownership or login requirement. Do not expose
the board publicly with personal notes. The optional admin route requires
a separately created superuser; no account or password is supplied.

`DEBUG` defaults to on and the fallback secret is deliberately a public
development value. A real deployment requires authentication/ownership,
a private `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, configured
`DJANGO_ALLOWED_HOSTS`, HTTPS, a production server, backups and static-file
hosting. `STICKY_DATABASE` can point to a separate local SQLite file.
Publishing the source repository does not deploy this application.
