#!/bin/bash
# creates the logdirs and logfiles, and adjusts their permissions

for instance in cronos cronos-dev; do
    logpath="/var/log/${instance}"
    [[ -d ${logpath} ]] || mkdir ${logpath}
    for level in info warning error critical; do
        logfile=${logpath}/${level}.log
        [[ -n ${logfile} ]] && touch ${logfile}
    done
    chmod 750 ${logpath}
    chmod 640 ${logpath}/*
    chown -R root:${instance} ${logpath}
done
