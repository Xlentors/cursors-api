# Cursors API

A read-only REST-API built with FastAPI meant for retrieving cursor metadata from cursors.dev.

## Features

- Retreive individual cursors by document ID
- Filter cursor by type and author
- Sort cursors by ID, name, and author
- Browse large sets of cursors with cursor-based pagination
- Validates API requests and responses with Pydantic

## Endpoints

- `GET /` — Returns a basic API message
- `GET /cursors` — Returns a collection of cursors
- `GET /cursors/{cursor_id}` — Returns one cursor by document ID

## Query Options

The `GET /cursors` endpoint supports these optional query parameters:

- `limit` — Number of cursors to return, from 1 to 50
- `cursor_type` — Filter by cursor type (for reference there are 4 cursor types: dot, circle, cross, misc)
- `cursor_author` — Filter by author
- `sort_by` — Sort by `id`, `name`, or `author`
- `sort_order` — Sort in `asc` or `desc` order
- `after_id` — Continue after the previous page's token

## Pagination

The API requests one more cursor than the selected limit to determine whether another page exists. If more results are available, it returns the last included cursor's ID as `next_page_token`.

Pass that token back as `after_id` to retrieve the next page:

```text
/cursors?limit=5&after_id=NEXT_PAGE_TOKEN
```

## Running Locally

Google Cloud credentials with access to the configured Firestore database are required.

```bash
git clone https://github.com/Xlentors/cursors-api.git
cd cursors-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
gcloud auth application-default login
fastapi dev main.py
```

Open `http://127.0.0.1:8000/docs` to test the API through FastAPI's interactive documentation.