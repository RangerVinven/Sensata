from typing import Annotated, Union

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder

from sqlalchemy.util import b64decode
from sqlmodel import Session, create_engine, select

import base64

from models import *


from json import JSONEncoder


class CustomJSONEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, SensorData):
            result = {}
            # copy data field and delete it from the object
            data = o.data
            del o.data
            result = jsonable_encoder(o)
            result["data"] = base64.b64encode(data).decode()
            return result

        return super().default(o)


app = FastAPI()


# read db url from .env file
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
DATABASE_URL = env_vars["DATABASE_URL"]
assert DATABASE_URL is not None

connect_args = {}
engine = create_engine(
    DATABASE_URL,
    echo=False,
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
async def read_root():
    return {"Hello": "World"}


# implement queries from ../chatgpt_query_design_response.txt
@app.get("/api/v1/data")
async def return_all_data(session: SessionDep):
    data = session.exec(
        select(SensorData)
        .order_by(SensorData.sensor_data_id.desc())
        .limit(50)
        .order_by(SensorData.sensor_data_id)
    ).all()
    return CustomJSONEncoder().encode(data)


from pydantic import BaseModel


class sensor_data_type(BaseModel):
    data: str
    sensor_key: uuid.UUID
    recorded_at: datetime


@app.post("/api/v1/data")
def add_data(json_sensor_data: sensor_data_type, session: SessionDep):
    # check if data is base64 encoded
    try:
        original_data = json_sensor_data.data
        decoded_data = b64decode(original_data)
    except:
        raise HTTPException(status_code=400, detail="Data is not base64 encoded")

    # create a new sensor data object
    # but first check if the sensor key exists
    sensor = session.exec(
        select(SensorTable).where(SensorTable.key == json_sensor_data.sensor_key)
    ).first()

    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor key not found")

    sensor_data = SensorData(
        data=decoded_data,
        time_recorded=json_sensor_data.recorded_at,
        time_added=datetime.now(),
        sensor_id_sensor_table=sensor.sensor_id,
        unique_id=uuid.uuid4(),
    )
    session.add(sensor_data)
    session.commit()
    session.refresh(sensor_data)
    return CustomJSONEncoder().encode(sensor_data)


class sensor_type(BaseModel):
    model_name: str | None
    manufacturer: str | None
    serial_number: str | None


@app.post("/api/v1/sensor")
async def add_sensor(sensor_data: sensor_type, session: SessionDep):
    # validate any(sensor_data.values())
    # add sensor to the database
    if not any(value is not None for value in vars(sensor_data).values()):
        raise HTTPException(status_code=400, detail="All fields are empty")

    sensor = SensorTable(
        sensor_model_name=sensor_data.model_name,
        manufacturer=sensor_data.manufacturer,
        serial_number=sensor_data.serial_number,
        key=uuid.uuid4(),
    )
    session.add(sensor)
    session.commit()
    session.refresh(sensor)
    return sensor
