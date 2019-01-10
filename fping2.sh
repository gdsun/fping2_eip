#!/bin/sh

dt=`date +%Y-%m%d-%H%M%S`
file=vm.lst

if [ ! -f fping2 ]
then
    echo "ERROR: Can't find fping2 binary."
    exit
fi

if [ "$#" != "1"  ]
then 
    echo "Usage: $0 [ip.lst]"
    exit
fi

file=$1
if [ ! -f $file ]
then
    echo "ERROR: Can't find $file."
    exit
fi

wc=`cat $file | wc -l`
if [ 200 -lt $wc ]
then
    echo "ERROR: too long ip.lst $wc > 200."
    exit
fi

detail_name="detail_${file}_${dt}.log"
summary_name="summary_${file}_${dt}.log"

chmod +x fping2

echo "Starting fping2   .....             CTRL+C to exit!"
./fping2 -i 0 -p 500 -t 1000 -l -D -s -f $file 2>$summary_name | tee -a $detail_name
#./fping2 -i 0 -p 50 -l -D -s -f $file

cat $summary_name

echo "=================================================="
echo "Detail see "$detail_name
echo "Summary see "$summary_name
echo "=================================================="

