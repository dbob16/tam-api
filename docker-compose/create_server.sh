!/bin/bash
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

echo "SS_MODE or Super Secure mode, locks each API key to the IP address it was generated with."
echo "Putting in something below will turn on SS_MODE. Leave blank and press enter to to leave it disabled."
read -p "SS_MODE? " ss_mode
if [[ "" == "$ss_mode" ]]; then
echo "# SS_MODE below if set to on locks the API keys to their original IP addresses" >> .env
echo "SS_MODE=off" >> .env
else
echo "# SS_MODE below if set to on locks the API keys to their original IP addresses" >> .env
echo "SS_MODE=on" >> .env
fi

docker compose up -d