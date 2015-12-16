#!/usr/bin/env bash
#Copyright (C) dirlt

for x in book/_sources/*.txt
do
    iconv -t utf-8 $x > $x.2
    mv $x.2 $x
done
