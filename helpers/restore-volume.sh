#!/bin/bash

print_usage() {
	echo "Usage: $0 <backup file> <docker volume>"
	exit 255
}

backup_file=$1
docker_volume=$2

if [ "$#" -ne 2 ]; then print_usage; fi
if [ ! -f "$backup_file" ]; then echo "File does not exist"; print_usage; fi
if [ "$(docker volume ls | grep -cw "$docker_volume")" -eq "0" ]; then echo "Volume not found"; print_usage; fi

docker run -it --rm \
  --entrypoint=/bin/sh \
  -v "$docker_volume":/from \
  -v "$(pwd)":/to \
  alpine \
  -c "rm -rf /from/*; tar -zxvf /to/$backup_file"
