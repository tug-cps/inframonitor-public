# Initial Setup, add data sources
1. Influxdb (native)
    1. Set `http://influxdb:8086` as server url
    2. Set `mqtt` as database
    3. Set `grafana` as user
    4. Set `grafana` as password (read access only)
    
2. MongoDB (third party plugin, already installed)
    1. Set `http://mongodb-proxy:3333` as server url
    2. Set `mongodb://grafana:grafana@mongodb:27017/?authSource=ontology` as mongodb url
    3. Set `ontology` as database