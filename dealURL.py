#-*- coding:utf-8 -*-
import re 
url = "http://ewww.hngp.gov.cn/henan/ggcx?appCode=H60&channelCode=0101&bz=1&pageSize=30"
def setPageSize(links):
    link = links[:]
    n = link.find("pageSize")
    m = link.find("pageNo")
    if n < 0 and m <0:
        link+= "&pageSize=30&pageNo=1"
    elif n <0 and m > 0:
        link = link[:m-1] + "&pageSize=30" + link[m-1:]
    elif n >0 and m >0:
        link =link[:n-1]+ "&pageSize=30"+link[m-1:]
    else : #(n>0,m<0)
        link =link[:n-1]+"&pageSize=30&pageNo=1"
    return link[:]
        
if __name__ == "__main__":
     global url
     print url
     print setPageSize(url)	