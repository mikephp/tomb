#!/usr/bin/env bash
#Copyright (C) dirlt

DATE=`date +%Y%m%d`
echo $DATE
./run_apps.py newrun $DATE
./queue_worker.py $DATE
./gen_report.py $DATE
