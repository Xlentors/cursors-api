from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Query
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1.field_path import FieldPath
from pydantic import BaseModel

PROJECT_ID = "cursors-925b4"

api = FastAPI()

db = firestore.Client(project=PROJECT_ID, database="testdb")

class Cursor(BaseModel):
    id: str
    name: str
    author: str
    type: str


class CursorPage(BaseModel):
    items: list[Cursor]
    next_page_token: str | None


@api.get("/")
def read_root():
    return {"message": "Hello, Cursor API!"}

@api.get("/cursors", response_model=CursorPage)
def read_cursors(
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    cursor_type: str | None = None,
    cursor_author: str | None = None,
    sort_by: Literal["id", "name", "author"] = "id",
    sort_order: Literal["asc", "desc"] = "asc",
    after_id: str | None = None,
):
    if sort_by == "id":
        sort_field = FieldPath.document_id()
    else:
        sort_field = sort_by

    if sort_order == "asc":
        direction = firestore.Query.ASCENDING
    else:
        direction = firestore.Query.DESCENDING

    cursor_query = db.collection("cursors").order_by(
        sort_field,
        direction=direction
    )

    if cursor_type is not None:
        cursor_query = cursor_query.where(
            filter=FieldFilter("type", "==", cursor_type)
        )

    if cursor_author is not None:
        cursor_query = cursor_query.where(
            filter=FieldFilter("author", "==", cursor_author)
        )

    if after_id is not None:
        after_snapshot = db.collection("cursors").document(after_id).get()

        if not after_snapshot.exists:
            raise HTTPException(status_code=400, detail="Invalid after_id")

        cursor_query = cursor_query.start_after(after_snapshot)

    cursor_snapshots = list(cursor_query.limit(limit + 1).stream())
    has_more = len(cursor_snapshots) > limit
    cursor_snapshots = cursor_snapshots[:limit]
    cursor_list = []

    for cursor_snapshot in cursor_snapshots:
        cursor_data = cursor_snapshot.to_dict()
        cursor_data["id"] = cursor_snapshot.id
        cursor_list.append(cursor_data)

    next_page_token = None

    if has_more:
        next_page_token = cursor_snapshots[-1].id

    return {
        "items": cursor_list,
        "next_page_token": next_page_token,
    }


@api.get("/cursors/{cursor_id}", response_model=Cursor)
def read_cursor(cursor_id: str):
    cursor_snapshot = db.collection("cursors").document(cursor_id).get()

    if not cursor_snapshot.exists:
        raise HTTPException(status_code=404, detail="Cursor not found")

    cursor_data = cursor_snapshot.to_dict()
    cursor_data["id"] = cursor_snapshot.id

    return cursor_data