#!/usr/bin/env bash
# Copyright (C) dirlt

PIDFILE=`pwd`/app.pid
kill `cat $PIDFILE`

ACCESS_LOG=`pwd`/log/access_log
ERROR_LOG=`pwd`/log/error_log
mkdir -p `pwd`/log/
sleep 2
gunicorn -w 8 -k gevent --worker-connections 1024 -b 127.0.0.1:10004 app:app --pid $PIDFILE --access-logfile $ACCESS_LOG --error-logfile $ERROR_LOG --daemon
