#!/bin/bash

print_usage() {
	echo "Usage: $0 <docker volume>"
	exit 255
}

docker_volume=$1
backup_file="backup-$docker_volume-$(date +%Y-%m-%d).tar.gz"

if [ "$#" -ne 1 ]; then	print_usage; fi
if [ "$(docker volume ls | grep -cw "$docker_volume")" -eq "0" ]; then echo "Volume not found"; print_usage; fi

docker run -it --rm \
  --entrypoint=/bin/sh \
  -v "$docker_volume":/from \
  -v "$(pwd)":/to \
  alpine \
  -c "tar -zcvf /to/$backup_file /from"
