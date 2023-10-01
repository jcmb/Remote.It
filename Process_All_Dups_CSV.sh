#!/bin/bash
rm DeviceList.csv

CRON=1
VENV=venv/Requests_Sig/bin/activate

if [ ! -z "$VENV" ]
then
    source $VENV
fi

./FullAccountReport.py @parameters/prod.key

if  [ $? != 0 ]
    then
    echo "Downloading of account data failed. Processing stopped"
    exit
fi

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


./RemoteIt-Delete.py  @RemoteIt.Params Production_Dups_To_Delete.csv
#./Production_Dups_To_Delete.sh
#./FullAccount.py  @parameters/prod.key > Production.csv
