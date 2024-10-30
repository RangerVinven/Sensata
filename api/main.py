from typing import Annotated, Union

from fastapi import FastAPI, Depends, HTTPException, Query

from sqlmodel import Session, create_engine, select


from models import *

app = FastAPI()


# read db url from .env file
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
DATABASE_URL = env_vars["DATABASE_URL"]
assert DATABASE_URL is not None

connect_args = {}
engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args=connect_args,
)

print(SQLModel.metadata.tables)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def read_root():
    return {"Hello": "World"}


# implement queries from ../chatgpt_query_design_response.txt
@app.get("/api/v1/data")
def return_all_data(session: SessionDep):
    data = session.exec(select(SensorData).limit(50)).all()
    return data
