#!/usr/bin/env bash

celery -A sibdev_test_2.celery beat -l ${LOG_LEVEL:-debug} --pidfile=
