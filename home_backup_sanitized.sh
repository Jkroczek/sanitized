#!/bin/bash
#
# Created by jkroczek 10.17.18
# usage:home_backup.sh <sync or backup>
#

#date variable to name folder for backup
currentdate=$(date +"%m_%d_%Y")

if [ $1 = "sync" ]; then
        echo "syncing your home to cloud"
        rsync -avzh --progress --delete --exclude=".*" --exclude="Downloads" --max-size=2G /home/jkroczek/ username@server:/home/username/
	date >> /home/jkroczek/scripts/home_backup.log # logs date and time of last sync
elif [ $1 = "backup" ]; then
        echo "creating a backup of your home"
        rsync -avzh --progress --exclude=".*" --exclude="Downloads" /home/username/ username@server:/home/username/backups/$currentdate/
else # catchall for bad input
        echo "nope try again."
fi