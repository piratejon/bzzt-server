create table source(
    id serial primary key,
    sequence uuid unique,
    network_address inet not null,
    uas text,
    added timestamp default now()
    );

create table accel(
    id serial primary key,
    fk_source integer references source(id) not null,

    sequence_id integer not null,
    loc geometry(POINT,4326) not null,
    zscore float not null
    );

create table notice(
    id serial primary key,
    fk_source integer references source(id) not null,

    loc geometry(POINT,4326) not null,
    message text not null
    );

