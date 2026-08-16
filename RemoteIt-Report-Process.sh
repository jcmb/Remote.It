#!/bin/bash
set -euo pipefail

REPORT_DIR="${REMOTEIT_REPORT_DIR:-/home/gkirk/Remote.It-Reports}"
WEB_ROOT="${REMOTEIT_WEB_ROOT:-/var/www/html/Remote.It}"

logger "$0 Started"

cd "$REPORT_DIR"
logger "$PWD"
logger "$USER"
PYVER="$(/usr/bin/env python3 --version)"
logger "Python: $PYVER"
logger "$PATH"
logger "Param: $1"
PATH="$PATH:/usr/local/bin/"
logger "$PATH"

if [ -z "${1:-}" ]; then
	echo "Usage: RemoteIt-Report-Process <Account> [skip-download]"
	exit 1
fi

account="$1"
download_ok=0

if [ -z "${2:-}" ]; then
	rm -f DeviceList.csv
	logger "Before Full Account"
	if python3 FullAccountReport.py "@parameters/${account}.key"; then
		download_ok=1
	fi
else
	download_ok=1
fi

if [ "$download_ok" -ne 1 ]; then
	logger "$0 Downloading of account ${account} data failed. Processing stopped"
	echo "Downloading of account ${account} data failed. Processing stopped"
	exit 1
fi

python3 RemoteIt-Report-Check.py --Devices

python3 RemoteIt-Report-Check.py --HTML --Invalid > Invalid.html
python3 RemoteIt-Report-Check.py --HTML --Services > Services.html
python3 RemoteIt-Report-Check.py --HTML --Changed > Changed.html

mv DeviceList.html Invalid.html Services.html Changed.html "${WEB_ROOT}/${account}"

./Filter_Report_CSV.sh

mv Problem.csv "${WEB_ROOT}/${account}"

date > date.html
date > date.txt

mv date.html date.txt DeviceList.csv "${WEB_ROOT}/${account}"
