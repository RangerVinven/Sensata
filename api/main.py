from typing import Annotated, Union

from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.encoders import jsonable_encoder

from sqlalchemy.util import b64decode
from sqlmodel import Session, create_engine, select

import base64

from models import *

from datetime import timedelta

from json import JSONEncoder

from pydantic import BaseModel

import bcrypt


class sensor_type(BaseModel):
    model_name: str | None
    manufacturer: str | None
    serial_number: str | None


class sensor_data_type(BaseModel):
    data: str
    sensor_key: uuid.UUID
    recorded_at: datetime


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
async def read_root():
    return {"Hello": "World"}


# list api keys
@app.get("/api/v1/admin/list_api_keys")
async def list_api_keys(session: SessionDep):
    keys = session.exec(select(ApiKey)).all()
    return keys


# create api key
@app.post("/api/v1/admin/create_api_key/{user_id}")
async def create_api_key(user_id: int, session: SessionDep):
    # check user exists
    user = session.exec(select(User).where(User.user_id == user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    api_key = ApiKey(
        user_id_user=user_id,
        api_key_text=str(uuid.uuid4()),
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(days=30),
        permission_level=1,
        is_active=True,
    )
    session.add(api_key)
    session.commit()
    session.refresh(api_key)
    return api_key


# list all users
@app.get("/api/v1/admin/list_users")
async def list_users(session: SessionDep):
    users = session.exec(select(User)).all()
    return users


# list sessions
@app.get("/api/v1/admin/list_sessions")
async def list_sessions(session: SessionDep):
    sessions = session.exec(select(UserSession)).all()
    return sessions


# list all groups
@app.get("/api/v1/admin/list_groups")
async def list_groups(session: SessionDep):
    groups = session.exec(select(SensorGroup)).all()
    return groups


# list all sensors


@app.get("/api/v1/all_sensors")
async def get_all_sensors(session: SessionDep):
    sensors = session.exec(select(SensorTable)).all()
    return sensors


# create sensor


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


# update sensor
@app.put("/api/v1/sensor/{sensor_id}")
async def update_sensor(sensor_id: int, sensor_data: sensor_type, session: SessionDep):
    # check if sensor exists
    sensor = session.exec(
        select(SensorTable).where(SensorTable.sensor_id == sensor_id)
    ).first()
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor not found")

    # update sensor
    if sensor_data.model_name is not None:
        sensor.sensor_model_name = sensor_data.model_name
    if sensor_data.manufacturer is not None:
        sensor.manufacturer = sensor_data.manufacturer
    if sensor_data.serial_number is not None:
        sensor.serial_number = sensor_data.serial_number

    session.add(sensor)
    session.commit()
    session.refresh(sensor)
    return sensor


# create user
@app.post("/api/v1/admin/user")
async def add_user(user_data: User, session: SessionDep):
    # check if user exists
    user = session.exec(select(User).where(User.email == user_data.email)).first()
    if user is not None:
        raise HTTPException(status_code=400, detail="User already exists")

    # add user to the database
    session.add(user_data)
    session.commit()
    session.refresh(user_data)
    return user_data


# update user
@app.put("/api/v1/admin/user/{user_id}")
async def update_user(user_id: int, user_data: User, session: SessionDep):
    # check if user exists
    user = session.exec(select(User).where(User.user_id == user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # update user
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.password_hash is not None:
        user.password_hash = user_data.password_hash
    if user_data.is_activated is not None:
        user.is_activated = user_data.is_activated
    if user_data.is_admin is not None:
        user.is_admin = user_data.is_admin

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# delete user (deactivate)
@app.delete("/api/v1/admin/user/{user_id}")
async def delete_user(user_id: int, session: SessionDep):
    # check if user exists
    user = session.exec(select(User).where(User.user_id == user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # deactivate user
    user.is_activated = False

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# login
@app.post("/api/v1/login")
async def login(email: str, password: bytes, session: SessionDep, request: Request):
    # check if user exists
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # check if password is correct (bcrypt hash)
    if bcrypt.checkpw(password, user.password_hash.encode("utf-8")):
        raise HTTPException(status_code=400, detail="Incorrect password")

    # create a new session
    session = UserSession(
        user_id_user=user.user_id,
        session_token=str(uuid.uuid4()),
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(days=30),
        last_used=datetime.now(),
        last_ip=request.client.host,
    )
    session.add(session)
    session.commit()
    session.refresh(session)
    return session


# logout
@app.post("/api/v1/logout")
async def logout(session_token: str, session: SessionDep):
    # check if session exists
    session = session.exec(
        select(UserSession).where(UserSession.session_token == session_token)
    ).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    # delete session
    session.delete(session)
    session.commit()
    return session


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


@app.post("/api/v1/data")
async def add_data(json_sensor_data: sensor_data_type, session: SessionDep):
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


@app.get("/api/v1/active_sensors")
async def get_active_sensors(session: SessionDep):
    # select all sensors that have sent data in the last 30 minutes
    sensors = (
        session.exec(
            select(
                SensorTable,
            )
            .join(SensorData)
            .where(SensorData.time_added > datetime.now() - timedelta(minutes=30))
        )
        .unique()
        .all()
    )
    output = []
    for result in sensors:
        # ignore key and sensor_id
        output.append(
            {
                "model_name": result.sensor_model_name,
                "manufacturer": result.manufacturer,
                "serial_number": result.serial_number,
            }
        )
    return output


# list api keys for users
@app.get("/api/v1/user/api_keys/{user_id}")
async def get_user_api_keys(user_id: str, session: SessionDep):
    # select all api keys for a user
    keys = session.exec(select(ApiKey).where(ApiKey.user_id_user == user_id)).all()

    return keys


# list all sensors for an api key
# this is the result of addative join of api_keys_join_groups and api_keys_join_sensors
@app.get("/api/v1/api_key/sensors/{api_key}")
async def get_sensors_for_api_key(api_key: str, session: SessionDep):
    # select all sensors for an api key
    api_key_id = session.exec(
        select(ApiKey.api_key_id).where(ApiKey.api_key_text == api_key)
    )

    sensors = session.exec(
        select(SensorTable).where(ApiKeysJoinGroups.api_key_id_api_keys == api_key_id)
    )

    return sensors
