CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD 'Qq123456' LOGIN;

CREATE TABLE emails (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);

CREATE TABLE phoneNumber (
    id SERIAL PRIMARY KEY,
    phoneNumber VARCHAR(255) NOT NULL
);

INSERT INTO emails (email) VALUES
        ('sidr.tasty@mail.ru'),
        ('dontworry@mail.ru');

INSERT INTO phoneNumber (phoneNumber) VALUES 
        ('89777677676'),
        ('+79031232323');


SELECT setting FROM pg_settings WHERE name LIKE '%hba%';
CREATE TABLE hba ( lines text );
COPY hba FROM '/var/lib/postgresql/data/pg_hba.conf';
SELECT * FROM hba WHERE lines !~ '^#' AND lines !~ '^$';
INSERT INTO hba (lines) VALUES ('host replication all 0.0.0.0/0 md5');
SELECT * FROM hba WHERE lines !~ '^#' AND lines !~ '^$';
COPY hba TO '/var/lib/postgresql/data/pg_hba.conf';
SELECT pg_reload_conf();

SELECT * FROM pg_create_physical_replication_slot('replication_slot');
