from typing import Annotated, Union

from fastapi import FastAPI, Depends, HTTPException, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.util import b64decode
from sqlmodel import Session, create_engine, select, union

import base64

from models import *

from datetime import timedelta

from json import JSONEncoder, dumps

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

# CORS Config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    """
    hello world
    """

    return {"Hello": "World"}


# list api keys
@app.get("/api/v1/admin/list_api_keys")
async def list_api_keys(session: SessionDep):
    """
    Lists all api keys

    todo: implement authentication and pagination
    """

    keys = session.exec(select(ApiKey)).all()
    return keys


# create api key
@app.post("/api/v1/admin/create_api_key/{user_id}")
async def create_api_key(user_id: int, session: SessionDep):
    """
    Create a new api key for a user

    todo: implement authentication
    """

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
    """
    List all users

    todo: implement authentication
    """
    users = session.exec(select(User)).all()
    return users


# list sessions
@app.get("/api/v1/admin/list_sessions")
async def list_sessions(session: SessionDep):
    """
    List all user sessions

    todo: implement authentication
    """
    sessions = session.exec(select(UserSession)).all()
    return sessions


# list all groups
@app.get("/api/v1/admin/list_groups")
async def list_groups(session: SessionDep):
    """
    List all sensor groups
    """
    groups = session.exec(select(SensorGroup)).all()
    return groups


# list all sensors
@app.get("/api/v1/all_sensors")
async def get_all_sensors(session: SessionDep):
    """
    Return all sensors
    """

    sensors = session.exec(select(SensorTable)).all()
    return sensors


# create sensor


@app.post("/api/v1/sensor")
async def add_sensor(sensor_data: sensor_type, session: SessionDep):
    """
    Add a new sensor to the database
    and return the sensor object
    """

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
    """
    Update sensor meta-data (only non-null fields are updated)
    """

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


class UserCreate(BaseModel):
    email: str
    password: str


# create user
@app.post("/api/v1/admin/user")
async def add_user(user_data: UserCreate, response: Response, session: SessionDep):
    """
    Add a new user to the database

    todo: document that password_hash is not hashed
    and is hashed on the server side using bcrypt
    todo: implement authentication
    """

    # check if user exists
    user = session.exec(select(User).where(User.email == user_data.email)).first()
    if user is not None:
        raise HTTPException(status_code=400, detail="User already exists")

    # validate password length
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=400, detail="Password length should be at least 8 characters"
        )
    elif len(user_data.password) > 60:
        raise HTTPException(
            status_code=400, detail="Password length should be at most 60 characters"
        )

    # valdiate email
    if "@" not in user_data.email:
        raise HTTPException(status_code=400, detail="Invalid email")

    # add user to the database
    # assume password isn't hashed
    hashed_password = bcrypt.hashpw(
        user_data.password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    db_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        is_activated=True,
        is_admin=False,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # create a new session

    user_session = UserSession(
        user_id_user=db_user.user_id,
        session_token=uuid.uuid4(),
        created_at=datetime.now(),
        last_used=datetime.now(),
        last_ip=request.client.host,
    )
    session.commit()
    session.refresh(user_session)

    response.set_cookie(key="session_token", value=str(user_session.session_token))

    return db_user


# set user as admin
@app.put("/api/v1/admin/user/{user_id}/set_admin")
async def set_user_as_admin(user_id: int, session: SessionDep):
    """
    Set a user as an admin
    """

    # check if user exists
    user = session.exec(select(User).where(User.user_id == user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_admin = True

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


class UserUpdate(BaseModel):
    email: str | None
    password: str | None


# update user
@app.put("/api/v1/admin/user/{user_id}")
async def update_user(user_id: int, user_data: UserUpdate, session: SessionDep):
    """
    Update user data (only non-null fields are updated)

    todo: document that password_hash is not hashed
    and is hashed on the server side using bcrypt
    todo: implement authentication
    """

    # check if user exists
    user = session.exec(select(User).where(User.user_id == user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # check if any fields are updated
    if user_data.email is None and user_data.password is None:
        raise HTTPException(
            status_code=400, detail="No fields are updated, nothing to update"
        )

    # update user
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.password is not None:
        # validate password length
        if len(user_data.password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Password length should be at least 8 characters",
            )
        elif len(user_data.password) > 60:
            raise HTTPException(
                status_code=400,
                detail="Password length should be at most 60 characters",
            )
        user.password_hash = bcrypt.hashpw(
            user_data.password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# delete user (deactivate)
@app.delete("/api/v1/admin/user/{user_id}")
async def delete_user(user_id: int, session: SessionDep):
    """
    Deactivate a user

    todo: implement authentication
    """

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
async def login(
    login_details: UserCreate, response: Response, session: SessionDep, request: Request
):
    """
    Login a user by creating a new session
    and returning the session token
    """

    # check if user exists
    user = session.exec(select(User).where(User.email == login_details.email)).first()
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")

    # check if password is correct (bcrypt hash)
    if not bcrypt.checkpw(
        login_details.password.encode("utf-8"), user.password_hash.encode("utf-8")
    ):
        raise HTTPException(status_code=400, detail="Incorrect password")

    # check if user is activated
    if not user.is_activated:
        raise HTTPException(status_code=400, detail="User was deactivated")

    # create a new session
    user_session = UserSession(
        user_id_user=user.user_id,
        session_token=uuid.uuid4(),
        created_at=datetime.now(),
        last_used=datetime.now(),
        last_ip=request.client.host,
    )
    session.add(user_session)
    session.commit()
    session.refresh(user_session)

    response.set_cookie(key="session_token", value=str(user_session.session_token))

    return {"status": "success"}


# logout
@app.post("/api/v1/logout")
async def logout(session_token: str, session: SessionDep):
    """
    Logout a user by deleting the session
    Doesn't log out other sessions (todo: implement another endpoint for that)
    """

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
    """
    Returns the last 50 sensor data entries in ascending order
    """

    data = session.exec(
        select(SensorData)
        .order_by(SensorData.sensor_data_id.desc())
        .limit(50)
        .order_by(SensorData.sensor_data_id)
    ).all()
    return CustomJSONEncoder().encode(data)


# Gets the sensor data for the given sensor
@app.get("/api/v1/sensor_data/{sensor_id}")
async def return_data_from_sensor(
    sensor_id: int, session: SessionDep, cursor: str = None, count: int = 50
) -> str:
    """
    Returns the last 50 sensor data entries in ascending order, for that given sensor

    cursor is the unique_id of the last element returned
    if there are no more elements, cursor will be "00000000-0000-0000-0000-000000000000"
    """

    if count > 100:
        count = 100

    if cursor is None:
        cursor = "00000000-0000-0000-0000-000000000000"

    data = session.exec(
        select(SensorData)
        .where(SensorData.sensor_id_sensor_table == sensor_id)
        .where(SensorData.unique_id > cursor)
        .order_by(SensorData.sensor_data_id.desc())
        .limit(count)
        .order_by(SensorData.sensor_data_id)
    ).all()

    if len(data) == 0:
        return Response(content="{}", media_type="application/json")

    next_cursor = data[-1].unique_id

    # if the last element is the same as the cursor, then there are no more elements
    if next_cursor == cursor:
        next_cursor = "00000000-0000-0000-0000-000000000000"

    ret_data = []
    for i in data:
        # extract into ret_data an object with the keys
        # data, time_recorded, time_added

        ret_data.append(
            {
                "data": base64.b64encode(i.data).decode(),
                "time_recorded": i.time_recorded,
                "time_added": i.time_added,
            }
        )

    ret_data = {"data": ret_data, "cursor": next_cursor}

    ret_data = dumps(ret_data, default=str)

    return Response(content=ret_data, media_type="application/json")


@app.post("/api/v1/data")
async def add_data(json_sensor_data: sensor_data_type, session: SessionDep):
    """
    Add sensor data to the database

    data is base64 encoded and will be rejected if it is not,
    server will decode the data and store it in the database
    """

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
    """
    Return all sensors that have sent data in the last 30 minutes
    """

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
    """
    List all api keys for a user
    """

    # select all api keys for a user
    keys = session.exec(select(ApiKey).where(ApiKey.user_id_user == user_id)).all()

    return keys


# list all sensors for an api key
# this is the result of addative join of api_keys_join_groups and api_keys_join_sensors
@app.get("/api/v1/api_key/sensors/{api_key}")
async def get_sensors_for_api_key(api_key: str, session: SessionDep):
    """
    todo: complete implementation, currently only returns sensors
    belonging to a group for an api key
    """

    # select all sensors for an api key
    api_key_id = session.exec(
        select(ApiKey.api_key_id).where(ApiKey.api_key_text == api_key)
    ).first()

    assert api_key_id is not None

    stmt_group = (
        select(SensorTable)
        .join(
            GroupJoinSensors,
            GroupJoinSensors.sensor_id_sensor_table == SensorTable.sensor_id,
        )
        .join(
            SensorGroup, GroupJoinSensors.group_id_sensor_groups == SensorGroup.group_id
        )
        .join(
            ApiKeysJoinGroups,
            ApiKeysJoinGroups.group_id_sensor_groups == SensorGroup.group_id,
        )
        .where(ApiKeysJoinGroups.api_key_id_api_keys == api_key_id)
    )

    stmt_sensor = (
        select(SensorTable)
        .join(
            ApiKeysJoinSensors,
            ApiKeysJoinSensors.sensor_id_sensor_table == SensorTable.sensor_id,
        )
        .where(ApiKeysJoinSensors.api_key_id_api_keys == api_key_id)
    )

    stmt = union(stmt_group, stmt_sensor)

    sensors = session.query(SensorTable).from_statement(stmt).all()

    return sensors


# get groups and sensors for an api key
@app.get("/api/v1/api_key/groups/{api_key}")
async def get_groups_for_api_key(api_key: str, session: SessionDep):
    """
    Get all groups and sensors for an api key
    """

    output = {"groups": [], "sensors": []}

    # select all groups for an api key
    api_key_id = session.exec(
        select(ApiKey.api_key_id).where(ApiKey.api_key_text == api_key)
    ).first()

    assert api_key_id is not None

    groups = (
        session.exec(
            select(SensorGroup)
            .join(
                ApiKeysJoinGroups,
                ApiKeysJoinGroups.group_id_sensor_groups == SensorGroup.group_id,
            )
            .where(ApiKeysJoinGroups.api_key_id_api_keys == api_key_id)
        )
        .unique()
        .all()
    )

    for group in groups:
        output["groups"].append(
            {
                "group_id": group.group_id,
                "group_name": group.group_name,
                "group_description": group.description,
            }
        )

    # select all sensors for an api key
    sensors = (
        session.exec(
            select(SensorTable)
            .join(
                ApiKeysJoinSensors,
                ApiKeysJoinSensors.sensor_id_sensor_table == SensorTable.sensor_id,
            )
            .where(ApiKeysJoinSensors.api_key_id_api_keys == api_key_id)
        )
        .unique()
        .all()
    )

    for sensor in sensors:
        output["sensors"].append(
            {
                "sensor_id": sensor.sensor_id,
                "model_name": sensor.sensor_model_name,
                "manufacturer": sensor.manufacturer,
                "serial_number": sensor.serial_number,
            }
        )

    return output


# create group
@app.post("/api/v1/group")
async def create_group(group_name: str, description: str, session: SessionDep):
    """
    Create a new sensor group
    """

    group = SensorGroup(
        group_name=group_name,
        description=description,
    )
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


# update group
@app.put("/api/v1/group/{group_id}")
async def update_group(
    group_id: int, group_name: str, description: str, session: SessionDep
):
    """
    Update a sensor group
    """

    # check if group exists
    group = session.exec(
        select(SensorGroup).where(SensorGroup.group_id == group_id)
    ).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    # update group
    group.group_name = group_name
    group.description = description

    session.add(group)
    session.commit()
    session.refresh(group)
    return group


# add sensor to group
@app.post("/api/v1/group/{group_id}/sensor/{sensor_id}")
async def add_sensor_to_group(group_id: int, sensor_id: int, session: SessionDep):
    """
    Add a sensor to a group
    """

    # check if group exists
    group = session.exec(
        select(SensorGroup).where(SensorGroup.group_id == group_id)
    ).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    # check if sensor exists
    sensor = session.exec(
        select(SensorTable).where(SensorTable.sensor_id == sensor_id)
    ).first()
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor not found")

    # add sensor to group
    group_join_sensor = GroupJoinSensors(
        group_id_sensor_groups=group_id,
        sensor_id_sensor_table=sensor_id,
    )
    session.add(group_join_sensor)
    session.commit()
    session.refresh(group_join_sensor)
    return group_join_sensor


# remove sensor from group
@app.delete("/api/v1/group/{group_id}/sensor/{sensor_id}")
async def remove_sensor_from_group(group_id: int, sensor_id: int, session: SessionDep):
    """
    Remove a sensor from a group
    """

    # check if group exists
    group = session.exec(
        select(SensorGroup).where(SensorGroup.group_id == group_id)
    ).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    # check if sensor exists
    sensor = session.exec(
        select(SensorTable).where(SensorTable.sensor_id == sensor_id)
    ).first()
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor not found")

    # remove sensor from group
    group_join_sensor = session.exec(
        select(GroupJoinSensors)
        .where(GroupJoinSensors.group_id_sensor_groups == group_id)
        .where(GroupJoinSensors.sensor_id_sensor_table == sensor_id)
    ).first()
    if group_join_sensor is None:
        raise HTTPException(status_code=404, detail="Sensor not in group")

    session.delete(group_join_sensor)
    session.commit()
    return group_join_sensor


# add sensor to api key
@app.post("/api/v1/api_key/{api_key}/sensor/{sensor_id}")
async def add_sensor_to_api_key(api_key: str, sensor_id: int, session: SessionDep):
    """
    Add a sensor to an api key
    """

    # check if api key exists
    api_key_id = session.exec(
        select(ApiKey.api_key_id).where(ApiKey.api_key_text == api_key)
    ).first()
    if api_key_id is None:
        raise HTTPException(status_code=404, detail="Api key not found")

    # check if sensor exists
    sensor = session.exec(
        select(SensorTable).where(SensorTable.sensor_id == sensor_id)
    ).first()
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor not found")

    # add sensor to api key
    api_key_join_sensor = ApiKeysJoinSensors(
        api_key_id_api_keys=api_key_id,
        sensor_id_sensor_table=sensor_id,
    )
    session.add(api_key_join_sensor)
    session.commit()
    session.refresh(api_key_join_sensor)
    return api_key_join_sensor


# add group to api key
@app.post("/api/v1/api_key/{api_key}/group/{group_id}")
async def add_group_to_api_key(api_key: str, group_id: int, session: SessionDep):
    """
    Add a group to an api key
    """

    # check if api key exists
    api_key_id = session.exec(
        select(ApiKey.api_key_id).where(ApiKey.api_key_text == api_key)
    ).first()
    if api_key_id is None:
        raise HTTPException(status_code=404, detail="Api key not found")

    # check if group exists
    group = session.exec(
        select(SensorGroup).where(SensorGroup.group_id == group_id)
    ).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    # add group to api key
    api_key_join_group = ApiKeysJoinGroups(
        api_key_id_api_keys=api_key_id,
        group_id_sensor_groups=group_id,
    )
    session.add(api_key_join_group)
    session.commit()
    session.refresh(api_key_join_group)
    return api_key_join_group


# remove sensor from api key
@app.delete("/api/v1/api_key/{api_key}/sensor/{sensor_id}")
async def remove_sensor_from_api_key(api_key: str, sensor_id: int, session: SessionDep):
    """
    Remove a sensor from an api key
    """

    # check if api key exists
    api_key_id = session.exec(
        select(ApiKey.api_key_id).where(ApiKey.api_key_text == api_key)
    ).first()
    if api_key_id is None:
        raise HTTPException(status_code=404, detail="Api key not found")

    # check if sensor exists
    sensor = session.exec(
        select(SensorTable).where(SensorTable.sensor_id == sensor_id)
    ).first()
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor not found")

    # remove sensor from api key
    api_key_join_sensor = session.exec(
        select(ApiKeysJoinSensors)
        .where(ApiKeysJoinSensors.api_key_id_api_keys == api_key_id)
        .where(ApiKeysJoinSensors.sensor_id_sensor_table == sensor_id)
    ).first()
    if api_key_join_sensor is None:
        raise HTTPException(status_code=404, detail="Sensor not in api key")

    session.delete(api_key_join_sensor)
    session.commit()
    return api_key_join_sensor


# remove group from api key
@app.delete("/api/v1/api_key/{api_key}/group/{group_id}")
async def remove_group_from_api_key(api_key: str, group_id: int, session: SessionDep):
    """
    Remove a group from an api key
    """

    # check if api key exists
    api_key_id = session.exec(
        select(ApiKey.api_key_id).where(ApiKey.api_key_text == api_key)
    ).first()
    if api_key_id is None:
        raise HTTPException(status_code=404, detail="Api key not found")

    # check if group exists
    group = session.exec(
        select(SensorGroup).where(SensorGroup.group_id == group_id)
    ).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    # remove group from api key
    api_key_join_group = session.exec(
        select(ApiKeysJoinGroups)
        .where(ApiKeysJoinGroups.api_key_id_api_keys == api_key_id)
        .where(ApiKeysJoinGroups.group_id_sensor_groups == group_id)
    ).first()
    if api_key_join_group is None:
        raise HTTPException(status_code=404, detail="Group not in api key")

    session.delete(api_key_join_group)
    session.commit()
    return api_key_join_group


# create api key
@app.post("/api/v1/admin/create_api_key/{user_id}")
async def create_api_key(user_id: int, session: SessionDep):
    """
    Create a new api key for a user
    """

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


# return if a user is an admin
@app.get("/api/v1/user/is_admin")
def get_is_admin(session_token: str, session: SessionDep):
    """
    Return if a user is an admin
    """

    # select user from session

    user = session.exec(
        select(User).where(UserSession.session_token == session_token)
    ).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {"is_admin": user.is_admin}
