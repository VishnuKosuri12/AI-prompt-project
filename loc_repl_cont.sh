#!/bin/bash

CONTAINER_NAME=$1

echo "--- down ---"
docker compose down $CONTAINER_NAME
echo "--- building ---"
docker compose build $CONTAINER_NAME
echo "--- up ---"
docker compose up -d $CONTAINER_NAME
echo "--- done ---"
echo ""
