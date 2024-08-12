#!/bin/bash -x

set -e
echo "test"
influx bucket create -n predictions -o $DOCKER_INFLUXDB_INIT_ORG -r 0 -t $DOCKER_INFLUXDB_INIT_ADMIN_TOKEN