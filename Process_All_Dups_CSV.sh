#!/bin/bash
logger $0 Started
rm DeviceList.csv
cd /home/IBSS/Remote.It

if [ ! -d Reports/Full ]
then
  mkdir -p Reports/Full
fi

if [ ! -d Reports/Date ]
then
  mkdir -p Reports/Date
fi


CRON=1
VENV=$HOME/venv/Requests_Sig/bin/activate

if [ ! -z "$VENV" ]
then
    source $VENV
fi


logger $0 Getting Full Account

./FullAccountReport.py @parameters/prod.key

if  [ $? != 0 ]
    then
    logger $0 "Downloading of account data failed. Processing stopped"
    echo "Downloading of account data failed. Processing stopped"
    exit
fi

logger $0 Computing Dups

./RemoteIt-CSV-Duplicates.py --CSV DeviceList.csv Production_Dups_To_Delete.csv

if [ -z "$CRON" ]
then
    echo "Start of duplicates to delete"
    cat ./Production_Dups_To_Delete.csv
    echo "End of duplicates to delete"
    wc -l ./Production_Dups_To_Delete.csv
    echo "Press any key to delete Duplicates. Ctrl-C to cancel"
    read -n 1
fi

logger $0 Deleting

./RemoteIt-Delete.py  @parameters/RemoteIt.Params Production_Dups_To_Delete.csv

current_date=$(date +"%Y-%m-%d")
current_month=$(date +"%Y-%m-01")
./RemoteIt-Account-Summary.py DeviceList.csv > Reports/Full/$current_date.txt
./RemoteIt-Account-Summary.py DeviceList.csv $current_month> Reports/Date/$current_date.txt

#./Production_Dups_To_Delete.sh
#./FullAccount.py  @parameters/prod.key > Production.csv

logger $0 Finished

