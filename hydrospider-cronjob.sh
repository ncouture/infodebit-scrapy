#!/bin/bash
# Executes a scrapy spider available in a virtualenv
#
# sleeplimit
#   random sleep limit in seconds or empty not to sleep
#
# virtualenv
#   absolute path to the spider's virtualenv
#
# scrapyroot
#   absolute path to the root of a scrapy project
#
# spiderfile
#   path to the spider file
#
# cronjoblog
#   empty for no logging or path to log file 

#set -x

sleeplimit="18000"
virtualenv="/home/self/dev/info-debit-virtualenv"
scrapyroot="/home/self/dev/info-debit-virtualenv/infodebit-scrapy"
spiderfile="/home/self/dev/info-debit-virtualenv/infodebit-scrapy/infodebit/spiders/hydrospider.py"
cronjoblog="$virtualenv/cronjob.log"

function log { 
    if [[ ! -z "$cronjoblog" ]]; then
	echo `date +"[%Y-%m-%d %T]"` "$@" >> $cronjoblog
    fi
}

function error {
    log "ERROR: $@"
    exit 1
}

function randomsleep {
    if [[ ! -z "$sleeplimit" ]]; then
	random_sleep="$(($RANDOM%$sleeplimit))"
	minutes=`echo "$random_sleep / 60" | bc`
	log "sleeping for $random_sleep seconds ($minutes minutes)..."
	sleep "$random_sleep"
    fi
}

function runspider {
    log "executing: scrapy runspider $spiderfile"
    scrapy runspider "$spiderfile" &>> $cronjoblog
}

log "`basename $0` starting"

if [[ ! -d "$virtualenv" ]]; then
    error "could not find virtualenv ($virtualenv)"
fi

activate="$virtualenv/bin/activate"

if [[ ! -f "$activate" ]]; then
    error "could not find bin/activate in $virtualenv"
fi


    
if [[ ! -d "$scrapyroot" ]]; then
    error "could not find the project root ($scrapyroot)" 
fi

log "activating virtualenv..."

source "$activate"

log "changing CWD to $scrapyroot"

cd "$scrapyroot"

randomsleep
runspider
