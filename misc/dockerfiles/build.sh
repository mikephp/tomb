#!/usr/bin/env bash
#Copyright (C) dirlt

build_base1404() {
    docker build -t tomb/ubuntu:base1404 base1404
}
build_home1404() {
    build_base1404
    docker build -t tomb/ubuntu:home1404 home1404
}
build_mysql() {
    build_base1404
    docker build -t tomb/ubuntu:mysql mysql
}
build_redis() {
    build_base1404
    docker build -t tomb/ubuntu:redis redis
}
build_base1204() {
    docker build -t tomb/ubuntu:base1204 base1204
}
build_home1204() {
    build_base1204
    docker build -t tomb/ubuntu:home1204 home1204
}

cmd=${1:-"null"}
case $1 in
    base1404)
        build_base1404
        ;;
    base1204)
        build_base1204
        ;;
    mysql)
        build_mysql
        ;;
    redis)
        build_redis
        ;;
    home1404)
        build_home1404
        ;;
    home1204)
        build_home1204
        ;;
    *)
        echo "wtf!"
        ;;
esac
