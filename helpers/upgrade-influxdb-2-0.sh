#!/bin/sh

echo "Pulling influxdb2 image"
docker image pull influxdb:2.0

# stop services
echo "Stopping services"
docker-compose down

# backup
echo "Backing up influxdb volume"
./helpers/backup-volume.sh influxdb

# create docker volume
echo "Creating influxdb2 volume"
docker volume create influxdb2

# give read permissions on directories in volume
echo "Giving all directories in influxdb volume read permissions"
docker run -it \
  --entrypoint=/bin/sh \
  -v influxdb:/volume/influxdb \
  alpine \
  -c "cd /volume/influxdb && find . -type d -exec chmod 755 {} +"

# Patch docker-compose files
echo "Backing up docker-compose.yml to docker-compose.yml.bak"
cp docker-compose.yml docker-compose.yml.bak
patch -i helpers/influxdb2.docker-compose.yml.diff
patch -i helpers/influxdb2.docker-compose.override.yml.diff

# ask for password
echo "Enter (new) password for admin user:"
read -r password

# run upgrade command
echo "Running influxdb2 upgrade command, restart your services if everything went alright!"
docker run -p 8086:8086 \
      -v influxdb:/var/lib/influxdb \
      -v influxdb2:/var/lib/influxdb2 \
      -e DOCKER_INFLUXDB_INIT_MODE="upgrade" \
      -e DOCKER_INFLUXDB_INIT_USERNAME="admin" \
      -e DOCKER_INFLUXDB_INIT_PASSWORD="$password" \
      -e DOCKER_INFLUXDB_INIT_ORG="tug-cps" \
      -e DOCKER_INFLUXDB_INIT_BUCKET="autogen" \
      influxdb:2.0