ARG base_image=python:3.9-slim
FROM $base_image

RUN pip install --upgrade pip
COPY common/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ARG service_name
COPY $service_name/requirements.txt /tmp/requirements-$service_name.txt
RUN pip install -r /tmp/requirements-$service_name.txt

COPY init_docker.sh /

WORKDIR /app
COPY common ./common/
COPY $service_name ./$service_name/

# enable color support
ENV TERM xterm-256color
# disable InsecureRequestWarning
ENV PYTHONWARNINGS ignore:Unverified HTTPS request

ENV service_name=$service_name
CMD ["/init_docker.sh"]
