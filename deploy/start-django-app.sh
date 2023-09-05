#!/usr/bin/env bash

gunicorn sibdev_test_2.wsgi --bind 0.0.0.0:8000
