from typing import List
from fastapi import Depends, FastAPI, HTTPException, Request, Response, WebSocket
from sqlalchemy.orm import Session
from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine
from fastapi.responses import HTMLResponse


models.Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Items</title>
    </head>
    <body>
        <h1>ФИО</h1>
        <form>
            <div class="row">
                <div class="six columns">
                    <label for="Name">ФИО</label>
                    <input class="u-full-width" type="email" placeholder="Иванов Иван Иванович" id="Name">
            </div>
            <div class="six columns">
                <label for="exampleRecipientInput">Вид мероприятия</label>
                <select class="u-full-width" id="exampleRecipientInput">
                    <option value="Option 1">Международное</option>
                    <option value="Option 2">всероссийское</option>
                    <option value="Option 3">ведомственное</option>
                    <option value="Option 4">региональное</option>
                </select>
            </div>
            <div class="six columns">
                <label for="SecondExample">Степень участия</label>
                <select class="u-full-width" id="SecondExample">
                    <option value="Option 1">индивидуальное</option>
                    <option value="Option 2">командное</option>
                </select>
            </div>
        </div>
        <input type="submit" value="отправить">
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/items/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@app.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = crud.create_item(db, item)
    return db_item


@app.get("/items/{item_id}")
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item_by_id(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    return crud.delete_item_by_id(db, item_id)


# @app.put("/items/{item_id} {field1} {field2}", response_model=schemas.Item)
# def update_item(item_id: int, field1: str, field2: str, db: Session = Depends(get_db)):
#     return crud.update_item_by_id(db, item_id, field1, field2)

@app.put("/items/", response_model=schemas.Item)
def update_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.update_item_by_id(db, item)
