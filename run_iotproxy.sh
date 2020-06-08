#!/bin/bash
#Start IotProxy in Docker

docker run -d \
    -p 8080:80 \
	--name iotproxy \
    --restart=unless-stopped \
    iotproxy
