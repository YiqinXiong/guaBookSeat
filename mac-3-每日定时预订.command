#! /bin/bash
basepath=$(cd `dirname $0`; pwd)
echo "1 22 * * * bash $basepath/mac-2-预约位置.sh" > $basepath/cron.cfg
crontab $basepath/cron.cfg
rm $basepath/cron.cfg