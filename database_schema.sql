-- Database generated with pgModeler (PostgreSQL Database Modeler).
-- pgModeler version: 1.1.4
-- PostgreSQL version: 16.0
-- Project Site: pgmodeler.io
-- Model Author: ---

-- Database creation must be performed outside a multi lined SQL file. 
-- These commands were put in this file only as a convenience.
-- 
-- object: sensor_database | type: DATABASE --
-- DROP DATABASE IF EXISTS sensor_database;
CREATE DATABASE sensor_database;
-- ddl-end --


-- object: public.auto_incrementing_user_id_sequence | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS public.auto_incrementing_user_id_sequence CASCADE;
CREATE SEQUENCE public.auto_incrementing_user_id_sequence
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;

-- ddl-end --
ALTER SEQUENCE public.auto_incrementing_user_id_sequence OWNER TO postgres;
-- ddl-end --

-- object: public.auto_incrementing_user_session_id_sequence | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS public.auto_incrementing_user_session_id_sequence CASCADE;
CREATE SEQUENCE public.auto_incrementing_user_session_id_sequence
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;

-- ddl-end --
ALTER SEQUENCE public.auto_incrementing_user_session_id_sequence OWNER TO postgres;
-- ddl-end --

-- object: public.auto_incrementing_sensor_data_id_sequence | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS public.auto_incrementing_sensor_data_id_sequence CASCADE;
CREATE SEQUENCE public.auto_incrementing_sensor_data_id_sequence
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;

-- ddl-end --
ALTER SEQUENCE public.auto_incrementing_sensor_data_id_sequence OWNER TO postgres;
-- ddl-end --

-- object: public.auto_incrementing_sensor_id_sequence | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS public.auto_incrementing_sensor_id_sequence CASCADE;
CREATE SEQUENCE public.auto_incrementing_sensor_id_sequence
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;

-- ddl-end --
ALTER SEQUENCE public.auto_incrementing_sensor_id_sequence OWNER TO postgres;
-- ddl-end --

-- object: public."user" | type: TABLE --
-- DROP TABLE IF EXISTS public."user" CASCADE;
CREATE TABLE public."user" (
	user_id smallint NOT NULL DEFAULT nextval('public.auto_incrementing_user_id_sequence'::regclass),
	email_address varchar(320) NOT NULL,
	password_hash varchar(60) NOT NULL,
	is_activated bool,
	is_admin bool,
	CONSTRAINT user_pk PRIMARY KEY (user_id)
);
-- ddl-end --
COMMENT ON COLUMN public."user".email_address IS E'RFC 2821 sets length of some mail commands at 256 characters so most emails will be less but the email standard allows for 64 characters (octets) in the "local part" (before the "@") and a maximum of 255 characters (octets) in the domain part (after the "@") for a total length of 320 characters';
-- ddl-end --
COMMENT ON COLUMN public."user".password_hash IS E'using bcrypt which has an output length of 59-60 depending on implementation, most using 60 for output';
-- ddl-end --
COMMENT ON COLUMN public."user".is_activated IS E'enabled/disabled';
-- ddl-end --
ALTER TABLE public."user" OWNER TO postgres;
-- ddl-end --

-- object: public.user_sessions | type: TABLE --
-- DROP TABLE IF EXISTS public.user_sessions CASCADE;
CREATE TABLE public.user_sessions (
	session_id smallint NOT NULL DEFAULT nextval('public.auto_incrementing_user_session_id_sequence'::regclass),
	created_at timestamp,
	last_used timestamp,
	user_id_user smallint,
	last_ip text,
	CONSTRAINT user_sessions_pk PRIMARY KEY (session_id)
);
-- ddl-end --
ALTER TABLE public.user_sessions OWNER TO postgres;
-- ddl-end --

-- object: public.sensor_table | type: TABLE --
-- DROP TABLE IF EXISTS public.sensor_table CASCADE;
CREATE TABLE public.sensor_table (
	sensor_id smallint NOT NULL DEFAULT nextval('public.auto_incrementing_sensor_id_sequence'::regclass),
	manufacturer text,
	serial_number text,
	model_name text,
	CONSTRAINT sensor_table_pk PRIMARY KEY (sensor_id)
);
-- ddl-end --
ALTER TABLE public.sensor_table OWNER TO postgres;
-- ddl-end --

-- object: public.sensor_data | type: TABLE --
-- DROP TABLE IF EXISTS public.sensor_data CASCADE;
CREATE TABLE public.sensor_data (
	sensor_data_id integer NOT NULL DEFAULT nextval('public.auto_incrementing_sensor_data_id_sequence'::regclass),
	data bytea NOT NULL,
	sensor_id_sensor_table smallint,
	CONSTRAINT sensor_data_id_pk PRIMARY KEY (sensor_data_id)
);
-- ddl-end --
COMMENT ON COLUMN public.sensor_data.data IS E'raw sensor data, up to user/server to parse sensor data';
-- ddl-end --
ALTER TABLE public.sensor_data OWNER TO postgres;
-- ddl-end --

-- object: public.auto_incrementing_sensor_group_id_sequence | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS public.auto_incrementing_sensor_group_id_sequence CASCADE;
CREATE SEQUENCE public.auto_incrementing_sensor_group_id_sequence
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;

-- ddl-end --
ALTER SEQUENCE public.auto_incrementing_sensor_group_id_sequence OWNER TO postgres;
-- ddl-end --

-- object: public.sensor_groups | type: TABLE --
-- DROP TABLE IF EXISTS public.sensor_groups CASCADE;
CREATE TABLE public.sensor_groups (
	group_id smallint NOT NULL DEFAULT nextval('public.auto_incrementing_sensor_group_id_sequence'::regclass),
	name text,
	description text,
	CONSTRAINT sensor_groups_pk PRIMARY KEY (group_id)
);
-- ddl-end --
ALTER TABLE public.sensor_groups OWNER TO postgres;
-- ddl-end --

-- object: public.auto_incrementing_api_key_id_sequence | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS public.auto_incrementing_api_key_id_sequence CASCADE;
CREATE SEQUENCE public.auto_incrementing_api_key_id_sequence
	INCREMENT BY 1
	MINVALUE 0
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;

-- ddl-end --
ALTER SEQUENCE public.auto_incrementing_api_key_id_sequence OWNER TO postgres;
-- ddl-end --

-- object: public.api_keys | type: TABLE --
-- DROP TABLE IF EXISTS public.api_keys CASCADE;
CREATE TABLE public.api_keys (
	api_key_id smallint NOT NULL DEFAULT nextval('public.auto_incrementing_api_key_id_sequence'::regclass),
	user_id_user smallint,
	created_at timestamp,
	expires_at timestamp,
	permission_level smallint,
	is_active bool,
	CONSTRAINT api_keys_pk PRIMARY KEY (api_key_id)
);
-- ddl-end --
COMMENT ON COLUMN public.api_keys.permission_level IS E'tbd which levels go to what.\nidea:\n0: daily statistics\n1: hourly statistics\n2: raw data since key created\n3: full raw data access';
-- ddl-end --
COMMENT ON COLUMN public.api_keys.is_active IS E'enabled/disabled';
-- ddl-end --
ALTER TABLE public.api_keys OWNER TO postgres;
-- ddl-end --

-- object: user_fk | type: CONSTRAINT --
-- ALTER TABLE public.api_keys DROP CONSTRAINT IF EXISTS user_fk CASCADE;
ALTER TABLE public.api_keys ADD CONSTRAINT user_fk FOREIGN KEY (user_id_user)
REFERENCES public."user" (user_id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: sensor_table_fk | type: CONSTRAINT --
-- ALTER TABLE public.sensor_data DROP CONSTRAINT IF EXISTS sensor_table_fk CASCADE;
ALTER TABLE public.sensor_data ADD CONSTRAINT sensor_table_fk FOREIGN KEY (sensor_id_sensor_table)
REFERENCES public.sensor_table (sensor_id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: public.api_keys_join_groups | type: TABLE --
-- DROP TABLE IF EXISTS public.api_keys_join_groups CASCADE;
CREATE TABLE public.api_keys_join_groups (
	group_id_sensor_groups smallint,
	api_key_id_api_keys smallint

);
-- ddl-end --
ALTER TABLE public.api_keys_join_groups OWNER TO postgres;
-- ddl-end --

-- object: sensor_groups_fk | type: CONSTRAINT --
-- ALTER TABLE public.api_keys_join_groups DROP CONSTRAINT IF EXISTS sensor_groups_fk CASCADE;
ALTER TABLE public.api_keys_join_groups ADD CONSTRAINT sensor_groups_fk FOREIGN KEY (group_id_sensor_groups)
REFERENCES public.sensor_groups (group_id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: api_keys_fk | type: CONSTRAINT --
-- ALTER TABLE public.api_keys_join_groups DROP CONSTRAINT IF EXISTS api_keys_fk CASCADE;
ALTER TABLE public.api_keys_join_groups ADD CONSTRAINT api_keys_fk FOREIGN KEY (api_key_id_api_keys)
REFERENCES public.api_keys (api_key_id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: public.api_keys_join_sensors | type: TABLE --
-- DROP TABLE IF EXISTS public.api_keys_join_sensors CASCADE;
CREATE TABLE public.api_keys_join_sensors (
	api_key_id_api_keys smallint,
	sensor_id_sensor_table smallint

);
-- ddl-end --
ALTER TABLE public.api_keys_join_sensors OWNER TO postgres;
-- ddl-end --

-- object: api_keys_fk | type: CONSTRAINT --
-- ALTER TABLE public.api_keys_join_sensors DROP CONSTRAINT IF EXISTS api_keys_fk CASCADE;
ALTER TABLE public.api_keys_join_sensors ADD CONSTRAINT api_keys_fk FOREIGN KEY (api_key_id_api_keys)
REFERENCES public.api_keys (api_key_id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: sensor_table_fk | type: CONSTRAINT --
-- ALTER TABLE public.api_keys_join_sensors DROP CONSTRAINT IF EXISTS sensor_table_fk CASCADE;
ALTER TABLE public.api_keys_join_sensors ADD CONSTRAINT sensor_table_fk FOREIGN KEY (sensor_id_sensor_table)
REFERENCES public.sensor_table (sensor_id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: public.group_join_sensors | type: TABLE --
-- DROP TABLE IF EXISTS public.group_join_sensors CASCADE;
CREATE TABLE public.group_join_sensors (
	group_id_sensor_groups smallint,
	sensor_id_sensor_table smallint

);
-- ddl-end --
ALTER TABLE public.group_join_sensors OWNER TO postgres;
-- ddl-end --

-- object: sensor_groups_fk | type: CONSTRAINT --
-- ALTER TABLE public.group_join_sensors DROP CONSTRAINT IF EXISTS sensor_groups_fk CASCADE;
ALTER TABLE public.group_join_sensors ADD CONSTRAINT sensor_groups_fk FOREIGN KEY (group_id_sensor_groups)
REFERENCES public.sensor_groups (group_id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: sensor_table_fk | type: CONSTRAINT --
-- ALTER TABLE public.group_join_sensors DROP CONSTRAINT IF EXISTS sensor_table_fk CASCADE;
ALTER TABLE public.group_join_sensors ADD CONSTRAINT sensor_table_fk FOREIGN KEY (sensor_id_sensor_table)
REFERENCES public.sensor_table (sensor_id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: user_fk | type: CONSTRAINT --
-- ALTER TABLE public.user_sessions DROP CONSTRAINT IF EXISTS user_fk CASCADE;
ALTER TABLE public.user_sessions ADD CONSTRAINT user_fk FOREIGN KEY (user_id_user)
REFERENCES public."user" (user_id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --


