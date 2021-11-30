#!/bin/bash
i=1
timee=0
jiange=150
while [ ${i} -le 5 ];
do
  now=`date "+%Y-%m-%d %H:%M:%S"`
  flag=`expr $timee % $jiange`
  if [ "$flag" -eq 0 ]
  then
  	ps -ef | grep "scrapy crawl ACM" | grep -v grep | awk '{print $2}' | xargs kill -9
  	sleep 2
	echo "${now}:已关闭爬虫"
  fi
  timee=`expr $timee + 1`
  count=`ps -fe |grep "scrapy crawl ACM"  | grep -v "grep" | wc -l`
  if [ "$count" -le 0 ]
  then
      nohup scrapy crawl ACM >> pachong.log &
      timee=1
      echo "${now}:启动爬虫"
  else
      echo "${now}:爬虫已运行"
  sleep 60
  fi
done
