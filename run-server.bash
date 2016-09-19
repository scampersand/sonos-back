#!/bin/bash

export FLASK_APP=sonos/app.py
export FLASK_DEBUG=1
flask run -h 0  # listen on all interfaces
