CREATE TABLE book(
    uuid character varying(255) PRIMARY KEY,
    title character varying(255),
    author character varying(255),
    language character varying(255),
    createtime timestamp without time zone,
    id bigint
);


CREATE TABLE log(
    id bigint PRIMARY KEY,
    client_id character varying(1024),
    session_id character varying(1024),
    user_id character varying(1024),
    country character varying(1024),
    user_agent character varying(1024),
    url character varying(1024),
    book_id character varying(1024),
    created_at timestamp without time zone
);


CREATE TABLE br_user(
    id character varying(256) PRIMARY KEY,
    usergender bigint, -- 0: unknown, 1: female, 2:male
    age bigint,
    createdat timestamp without time zone,
    updatedat timestamp without time zone
);


CREATE TABLE countries(
    name character varying(255),
    code character(4) PRIMARY KEY
);


CREATE TABLE languages(
    code character (4) PRIMARY KEY,
    name character varying(255),
    name_revert character varying(255)
);


CREATE TABLE IF NOT EXISTS gender(
    code smallint PRIMARY KEY,
    name character (8)
);


CREATE TABLE reading_by_country(
    country_name character varying(255) PRIMARY KEY,
    title character varying(255),
    readers_in_country bigint
);


CREATE TABLE reading_by_language(
    language_name character varying(255) PRIMARY KEY,
    books_read bigint,
    pages_read bigint
);


CREATE TABLE reading_by_gender(
    gender_name character varying(255) PRIMARY KEY,
    books_read bigint,
    pages_read bigint,
    pages_per_book numeric
);


CREATE TABLE search_summary(
    term character varying(1024) PRIMARY KEY,
    number_of_searches bigint
);
