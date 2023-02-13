from asyncio import current_task
from statistics import median
from typing import Optional
from click import echo
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse # html 파일을 전송하고 싶음
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import pymysql
from regex import F
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from FastAPI.model import camuser
from FastAPI.example1 import getCameraStream
# from central_2 import getCameraStream

# sqlalchemy 사용
HOSTNAME = 'localhost'
PORT = 3306
USERNAME = 'root'
PASSWORD = 'tjdals2316393!'
DBNAME = 'camuser'

MYSQL_URL = f'mysql+aiomysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DBNAME}'
engine = create_async_engine(MYSQL_URL, echo=True) # echo가 sql log가 찍히게 하는 거
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
session = async_scoped_session(async_session, scopefunc=current_task)

# ------------------------------------------------------

app = FastAPI()
templates = Jinja2Templates(directory="FastAPI")

@app.get("/")
def read_root():
    return {"Hello":"World"}

@app.get("/items/{item_id}")
def read_item(item_id: str, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}
#http://localhost:8000/items/4?q=qwe

@app.get("/htmlE")
def read_html():
    print("html request")
    return FileResponse('FastAPI/html/index.html')
# {
#     name:["aaaa", "bbasda"],
#     median:"aaaaaa"
# }
@app.get("/htmlEe", response_class=FileResponse)
async def read_html(request: Request):
    query = select(
        camuser.name,
        camuser.median)
    result = await session.execute(query)
    result_a = result.all() # result_a[0]이 처음 row [0][0]이 row의 첫 column
    print("html request")
    return templates.TemplateResponse("html/index.html", {"request":request, "name":result_a[0][0], "median":int(result_a[0][1])})

@app.get("/css")
def read_html():
    print("css request")
    return FileResponse('FastAPI/html/style.css')

@app.get("/video")
def read_vid():
    return StreamingResponse(getCameraStream(), 
                media_type="multipart/x-mixed-replace; boundary=PNPframe")

@app.get("/dbdb")
async def read_db():
    query = select(
        camuser.name,
        camuser.median)
    result = await session.execute(query)
    result_a = result.all() # result_a[0]이 처음 row [0][0]이 row의 첫 column
    return result_a
