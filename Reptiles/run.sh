#!/bin/bash
i=1
timee=0
jiange=150
source=$1
echo "爬取源:${source}"
while [ ${i} -le 5 ];
do
  now=`date "+%Y-%m-%d %H:%M:%S"`
  flag=`expr $timee % $jiange`
  if [ "$flag" -eq 0 ]
  then
  	ps -ef | grep "scrapy crawl ${source}" | grep -v grep | awk '{print $2}' | xargs kill -9
  	sleep 2
  fi
  timee=`expr $timee + 1`
  count=`ps -fe |grep "scrapy crawl ${source}"  | grep -v "grep" | wc -l`
  if [ "$count" -le 0 ]
  then
      nohup scrapy crawl ACM >> /dev/null &
      timee=1
      echo "${now}:启动爬虫"
  else
      echo "${now}:爬虫已运行"
  sleep 60
  fi
done
