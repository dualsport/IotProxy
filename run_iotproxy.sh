#!/bin/bash
#Start IotProxy in Docker

docker run -d \
    -p 8080:80 \
    --restart=unless-stopped \
    iotproxy
