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


from pydantic import BaseModel


class sensor_data_type(BaseModel):
    data: bytes
    sensor_key: uuid.UUID
    recorded_at: datetime


@app.post("/api/v1/data")
def add_data(json_sensor_data: sensor_data_type, session: SessionDep):
    # create a new sensor data object
    # but first check if the sensor key exists
    sensor = session.exec(
        select(SensorTable).where(SensorTable.key == json_sensor_data.sensor_key)
    ).first()

    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor key not found")

    sensor_data = SensorData(
        data=json_sensor_data.data,
        time_recorded=json_sensor_data.recorded_at,
        time_added=datetime.now(),
        sensor_id_sensor_table=sensor.sensor_id,
        unique_id=uuid.uuid4(),
    )
    session.add(sensor_data)
    session.commit()
    return sensor_data
