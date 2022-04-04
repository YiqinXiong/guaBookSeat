#! /bin/bash
basepath=$(cd `dirname $0`; pwd)
echo "0 22 * * * $basepath/mac-2-预约位置.command" > $basepath/cron.cfg
crontab $basepath/cron.cfg
rm $basepath/cron.cfg