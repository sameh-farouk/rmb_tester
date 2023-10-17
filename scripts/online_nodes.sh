#!/bin/bash

# query gridproxy for nodes with status `up` and retrun a list of nodes' twin ids

url="https://gridproxy.dev.grid.tf/nodes?status=up"

response=$(curl -s -X 'GET' \
  "$url" \
  -H 'accept: application/json')

twinIds=$(echo "$response" | jq -r '.[] | .twinId')

echo "${twinIds[*]}" | tr '\n' ' '

