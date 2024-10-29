from typing import Annotated, Union

from fastapi import FastAPI, Depends, HTTPException, Query

from sqlmodel import Field, Session, SQLModel as _SQLModel, create_engine, select

from sqlalchemy.orm import declared_attr

from fastapi_utils.camelcase import camel2snake


class SQLModel(_SQLModel):

    @declared_attr
    def __tablename__(cls) -> str:
        return camel2snake(cls.__name__)


app = FastAPI()


# Define user table
# user_id: smallint primary key autoincrement
# email 320 varchar not null
# password_hash varchar 60 not null
# is_activated boolean
# is_admin boolean
class User(SQLModel, table=True):
    user_id: int = Field(default=None, primary_key=True)
    email: str
    password_hash: str
    is_activated: bool | None
    is_admin: bool | None


# Define user_sessions table
# session_id: smallint primary key autoincrement
# created_at: timestamp
# last_used: timestamp
# last_ip: text
# user_id_user: smallint foreign key
class UserSession(SQLModel, table=True):
    session_id: int = Field(default=None, primary_key=True)
    created_at: str | None
    last_used: str | None
    last_ip: str | None
    user_id_user: int = Field(foreign_key="user.user_id")


# Define api_keys table
# api_key_id: smallint primary key autoincrement
# user_id_user: smallint foreign key
# created_at: timestamp
# expires_at: timestamp
# permission_level: smallint
# is_active: boolean
# api_key_text: text (uuidv4)
class ApiKey(SQLModel, table=True):
    api_key_id: int = Field(default=None, primary_key=True)
    user_id_user: int = Field(foreign_key="user.user_id")
    created_at: str | None
    expires_at: str | None
    permission_level: int | None
    is_active: bool | None
    api_key_text: str | None


# Define sensor_groups table
# group_id: smallint primary key autoincrement
# group_name: text
# description: text
class SensorGroup(SQLModel, table=True):
    group_id: int = Field(default=None, primary_key=True)
    group_name: str | None
    description: str | None


# Define sensor_table table
# sensor_id: smallint primary key autoincrement
# manufacturer: text
# serial_number: text
# model_name: text
class SensorTable(SQLModel, table=True):
    sensor_id: int = Field(default=None, primary_key=True)
    manufacturer: str | None
    serial_number: str | None
    sensor_model_name: str | None


# Define sensor_data table
# sensor_data_id: integer primary key autoincrement
# data: bytea
# sensor_id_sensor_table: smallint foreign key
# time_recorded: timestamp
# time_added: timestamp
# unique_id: text (uuidv4)
class SensorData(SQLModel, table=True):
    sensor_data_id: int = Field(default=None, primary_key=True)
    data: bytes | None
    sensor_id_sensor_table: int = Field(foreign_key="sensor_table.sensor_id")
    time_recorded: str | None
    time_added: str | None
    unique_id: str | None


# Define many to many relationship between api_keys and sensor_groups,
# sensor_groups and sensor_table, api_keys and sensors


# table names: api_keys_join_groups, api_keys_join_sensors, group_join_sensors
# api_keys_join_groups
# api_key_id_api_keys: smallint foreign key
# group_id_sensor_groups: smallint foreign key
class ApiKeysJoinGroups(SQLModel, table=True):
    api_key_id_api_keys: int = Field(foreign_key="api_key.api_key_id", primary_key=True)
    group_id_sensor_groups: int = Field(
        foreign_key="sensor_group.group_id", primary_key=True
    )


# api_keys_join_sensors
# api_key_id_api_keys: smallint foreign key
# sensor_id_sensor_table: smallint foreign key
class ApiKeysJoinSensors(SQLModel, table=True):
    api_key_id_api_keys: int = Field(foreign_key="api_key.api_key_id", primary_key=True)
    sensor_id_sensor_table: int = Field(
        foreign_key="sensor_table.sensor_id", primary_key=True
    )


# group_join_sensors
# group_id_sensor_groups: smallint foreign key
# sensor_id_sensor_table: smallint foreign key
class GroupJoinSensors(SQLModel, table=True):
    group_id_sensor_groups: int = Field(
        foreign_key="sensor_group.group_id", primary_key=True
    )
    sensor_id_sensor_table: int = Field(
        foreign_key="sensor_table.sensor_id", primary_key=True
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
