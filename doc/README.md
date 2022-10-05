# Initial setup steps

1. Copy `alert/secret.env.example` to `/srv/alert/secret.env`, adapt values
2. Copy `grafana/secret.env.example` to `/srv/grafana/secret.env`, adapt values
3. Copy `inframonitor_common/secret.env.example` to `/srv/inframonitor_common/secret.env`, adapt values
4. Copy server ssl certs to /srv/certs
5. Start influxdb and mongodb in debug mode (without authentication)
   
   `docker-compose -f docker-compose.yml -f docker-compose.dev -d influxdb mongodb`
6. Create users for influxdb and mongodb as documented in `influxdb.influx` and `mongodb.mongo`

   * To connect to the influxdb shell: `docker-compose execute influxdb influx`
   * To connect to the mongodb shell: `docker-compose execute mongodb mongo`
    
7. Stop all containers with `docker-compose down`
8. Start all containers in production mode with `docker-compose up -d`
9. After some seconds check that all containers are up with `docker-compose ps`
