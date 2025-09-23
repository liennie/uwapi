#!/usr/bin/env bash

source venv/bin/activate
source .env

UNNATURAL_CONNECT_ADDR=${1:-127.0.0.1} UNNATURAL_CONNECT_PORT=${2:-12345} python main.py
