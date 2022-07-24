#!/bin/bash
FILE=.env.dev
docker-compose --env-file $FILE up -d --build