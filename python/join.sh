#!/usr/bin/env bash

source venv/bin/activate
source .env

if [ -z "$1" ]; then
	echo "missing lobby id"
	exit 1
fi

UNNATURAL_CONNECT_LOBBY=$1 python main.py
