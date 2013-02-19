#!/bin/bash

exit_usage() {
    echo "Usage: db_backup.sh database_name output_folder scp_path"
    echo ""
    echo "database_name: database to backup"
    echo "output_folder: where the backup will be stored"
    echo "scp_path: where to copy using scp, need access via ssh keys"
    echo ""
    echo "You can add this via crontab like: "
    echo "0 0 * * * /opt/openerp-idu-addons/utils/db_backup.sh openerp-db /backup/ usr@machine:bk/"
    exit 1
}

case $# in
    3 ) dbname=$1
        folder=$2
        scp_path=$3;; #Needs access via ssh keys
    * ) exit_usage;;
esac

date=$(date +%Y%m%d)
logfile="$folder/$dbname$date.sql"

#TODO: Add rotation
pg_dump $dbname -f $logfile
scp $logfile $scp_path
