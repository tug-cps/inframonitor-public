FROM alpine AS builder
WORKDIR /tmp/build
RUN wget -q -O master.zip https://github.com/JamesOsgood/mongodb-grafana/archive/master.zip && unzip master.zip && rm master.zip

FROM grafana/grafana-oss:9.2.2
ENV GF_PLUGIN_DIR=/usr/local/grafana/plugins
ENV GF_PATHS_PLUGINS=$GF_PLUGIN_DIR
ENV GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS=grafana-mongodb-datasource

USER root
RUN mkdir -p $GF_PLUGIN_DIR && chown grafana:root $GF_PLUGIN_DIR
USER grafana

COPY --chown=grafana:root --from=builder /tmp/build/mongodb-grafana-master $GF_PLUGIN_DIR/mongodb-grafana
RUN grafana-cli plugins install grafana-worldmap-panel
RUN grafana-cli plugins install speakyourcode-button-panel

HEALTHCHECK CMD wget --no-verbose --tries=1 --spider localhost:3000/api/health || exit 1
