#!/bin/bash
grep -v -E "EC520.*YU_Web_Proxy_80" DeviceList.csv > List.1
grep -v -E "EC520.*YU_SSH_22"  List.1 > List.2
grep -v -E "EC520.*YU_Internal_SSH_22" List.2 > List.2.5
grep -v -E "EC520.*YU,"  List.2.5 > List.3

grep -v -E "SNM941-.* - Internal_TCP_1" List.3 > List.4
grep -v -E "SNM941-.* - Internal_TCP_2" List.4 > List.5
grep -v -E "SNM941-.* - Internal_SSH"   List.5 > List.6
grep -v -E "SNM941-.* - Internal_HTTP"  List.6 > List.7

grep -v -E "SNM941-.* - External_TCP_1" List.7 > List.8
grep -v -E "SNM941-.* - External_TCP_2" List.8 > List.9
grep -v -E "SNM941-.* - External_VNC"   List.9 > List.10
grep -v -E "SNM941-.* - External_HTTP"  List.10 > List.11
grep -v -E "SNM941-.* - External_HTTPS" List.11 > List.12
grep -v -E "SNM941-.* - External_SSH"   List.12 > List.13
grep -v -E "SNM941-....F.....,"         List.13 > List.14
grep -v -E "SNM941-....7.....,"         List.14 > List.15

grep -v -E "Tablet-.* - VNC"            List.15 > List.16
grep -v -E "Tablet-[a-zA-Z0-9\-]*,"       List.16 > List.17

cp List.17 List.17.csv

open List.17.csv

#grep -v -E "EC520.*ZZ,"  List.17 > List.18
#grep -v -E "EC520.*ZZ_Web_Proxy_80" List.18 > List.19
#grep -v -E "EC520.*ZZ_Internal_SSH_22" List.19 > List.20

#cp List.20 List.20.csv

#open List.20.csv

