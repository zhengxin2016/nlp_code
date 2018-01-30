#!/usr/bin/env bash

NAME='server_develop.py'
echo "process name: $NAME"
ID=`ps -aux | grep "$NAME" | grep -v "grep" | awk '{print $2}'`
for id in $ID
    do
        kill -9  $id
        echo "  => killed $id"
    done
echo 'restart...'
nohup python3 server_develop.py > server.log 2>&1 &
PROCESS=`ps -aux | grep "$NAME" | grep -v "grep"`
echo "  => $PROCESS"
echo 'finished!'
