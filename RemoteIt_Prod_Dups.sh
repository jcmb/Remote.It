#! /bin/bash
./FullAccount.py  @parameters/prod.key > Production.csv

if  [ $? != 0 ]
    then
    echo "Downloading of account data failed. Processing stopped"
    exit
fi

    
./RemoteIt-Account-Duplicates.py Production.csv Production_Dups_To_Delete.sh
echo "Start of duplicates to delete"
cat ./Production_Dups_To_Delete.sh
echo "End of duplicates to delete"
echo "Press any key to delete Duplicates. Ctrl-C to cancel"
read -n 1
./Production_Dups_To_Delete.sh
./FullAccount.py  @parameters/prod.key > Production.csv
