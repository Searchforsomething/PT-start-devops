FROM postgres:14-alpine 

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=Qq123456
ENV POSTGRES_DB=pt_bot_db
ENV POSTGRES_HOST_AUTH_METHOD=scram-sha-256
ENV POSTGRES_INITDB_ARGS="--auth-host=scram-sha-256"
ENV POSTGRES_CONFIG="log_replication_commands = on"


COPY ./init.sql /docker-entrypoint-initdb.d/init.sql

EXPOSE 5432
