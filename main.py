from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import firestore

PROJECT_ID = "cursors-925b4"

api = FastAPI()

db = firestore.Client(project=PROJECT_ID, database="testdb")

class Cursor(BaseModel):
    id: str
    name: str
    author: str
    type: str

@api.get("/")
def read_root():
    return {"message": "Hello, Cursor API!"}


@api.get("/cursors", response_model=list[Cursor])
def read_cursors():
    cursor_snapshots = db.collection("cursors").limit(10).stream()
    cursor_list = []
    
    for cursor_snapshot in cursor_snapshots:
        cursor_data = cursor_snapshot.to_dict()
        cursor_data["id"] = cursor_snapshot.id
        cursor_list.append(cursor_data)
    
    return cursor_list

@api.get("/cursors/{cursor_id}", response_model=Cursor)
def read_cursor(cursor_id: str):
    cursor_snapshot = db.collection("cursors").document(cursor_id).get()
    
    if not cursor_snapshot.exists:
        raise HTTPException(status_code=404, detail="Cursor not found")
    
    cursor_data = cursor_snapshot.to_dict()
    cursor_data["id"] = cursor_snapshot.id
    
    return cursor_data