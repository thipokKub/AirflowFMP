#!/bin/bash

# Initialize environment
mkdir -p ./dags ./logs ./plugins ./data ./data/mysql ./data
sudo chown 999:999 ./data/mysql
sudo chmod 777 ./data/mysql

FILE=.env.dev
if test -f "$FILE"; then
    grep -v "AIRFLOW_UID=" $FILE > .env_temp; mv .env_temp $FILE
    grep -v "AIRFLOW_GID=" $FILE > .env_temp; mv .env_temp $FILE
    { echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0"; cat $FILE; } > .env_temp; mv .env_temp $FILE
else
    # Only ensure that airflow system is up and running
    echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > $FILE
fi

# Initialize docker-compose system
docker-compose --env-file $FILE up airflow-init
