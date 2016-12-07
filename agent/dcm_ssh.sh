#!/bin/bash

USER=$1
HOST=$2
PORT=$3
KEY=$4
FILE=$5
DIR=$6

scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=no -P $PORT -i $KEY $5 $USER@$HOST:$DIR
