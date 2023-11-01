#!/bin/bash

# query gridproxy for the registred nodes and retrun a list of nodes' twin IDs

if [[ "$1" == "--likely-up" ]]; then
  url="https://gridproxy.dev.grid.tf/nodes?status=up&size=1000"
elif [[ "$1" == "--likely-down" ]]; then
  url="https://gridproxy.dev.grid.tf/nodes?status=down&size=1000"
else
  url="https://gridproxy.dev.grid.tf/nodes?size=1000"
fi

response=$(curl -s -X 'GET' \
  "$url" \
  -H 'accept: application/json')

twinIds=$(echo "$response" | jq -r '.[] | .twinId')

echo "${twinIds[*]}" | tr '\n' ' '
