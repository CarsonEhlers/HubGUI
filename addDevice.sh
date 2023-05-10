#!/bin/bash

# get args
deviceId=$1
code=$2

# set filename to temp- + deviceId + .txt
filename="temp-$deviceId.txt"

# get start time to be able to calculate elapsed time
start=$(date +%s%N)

# print hello
echo "$deviceId - addDevice bash script started"

# get current time
now=$(date +"%T")

# delete $filename only if it exists
if [ -f "$filename" ]; then
    rm $filename
fi

# get temperature
~/matter/MoistureSensorFirmware/esp-matter/connectedhomeip/connectedhomeip/out/host/chip-tool pairing code $deviceId $code --commissioner-name 5 > $filename

# get elapsed time since start
elapsedTime=$((($(date +%s%N) - $start)/1000000))

# print elapsed time
echo "Elapsed time: $elapsedTime ms"