#!/bin/bash

if [ "$RUN_MODE" = "internal" ]
then
  echo "Running in Internal Mode"
  python3 /scripts/internal.py &
fi

if [ "$RUN_MODE" = "external" ]
then
  echo "Running in External Mode"
  python3 /scripts/external.py &
fi