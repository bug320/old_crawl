# crawl重写方案
---
##　需求目标:
　1. 从采购网　seeｄ_url　中　爬下全部中标结果。
  2. 以字段 “序号”，“url”，“标题”，“时间” 的形式 存入 mysql 数据库
  3. 以字段 "序号","url","结果正文" 的形式存入 hbase 数据库
  4. 每天固定时间开始爬网站，并查中标结果是否更新，把更新内容保存到 数据库中
  5. 如果在爬取过程中出现中断，显示中断原因，并且设置断点，并且再次启动爬虫时候从断点出开始爬取
  
