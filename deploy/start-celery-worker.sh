#!/usr/bin/env bash

celery -A sibdev_test_2.celery worker --loglevel=${LOG_LEVEL:-debug}
