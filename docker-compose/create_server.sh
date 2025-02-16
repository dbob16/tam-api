#!/bin/bash
cd certs
./gen_certs.sh
cd ..

echo "# This is the database information." > .env
echo "DB_USER=tam" >> .env
echo "DB_PASSWORD=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 20 | head -n 1)" >> .env
echo "DB_NAME=tam" >> .env
echo "DB_LOC=./db-data" >> .env
echo "" >> .env
echo "If you wish to enable API keys and set a password, enter it here."
read -p "API_PW: " api_pw
echo "# This is the API security section" >> .env
echo "API_PW=$api_pw" >> .env

docker compose up -d