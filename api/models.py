from sqlmodel import SQLModel as _SQLModel, Field
from fastapi_utils.camelcase import camel2snake
from sqlalchemy.orm import declared_attr
from datetime import datetime
from pydantic import EmailStr
import uuid


class SQLModel(_SQLModel):

    @declared_attr
    def __tablename__(cls) -> str:
        return camel2snake(cls.__name__)


# Define user table
# user_id: smallint primary key autoincrement
# email 320 varchar not null
# password_hash varchar 60 not null
# is_activated boolean
# is_admin boolean
class User(SQLModel, table=True):
    user_id: int = Field(default=None, primary_key=True)
    email: EmailStr
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
    created_at: datetime | None
    last_used: datetime | None
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
    created_at: datetime | None
    expires_at: datetime | None
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
    key: uuid.UUID | None


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
    time_recorded: datetime | None
    time_added: datetime | None
    unique_id: uuid.UUID | None


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
