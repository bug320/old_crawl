#-*- coding:utf-8 -*-
from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
import urllib2
import re
import urlparse
import csv

# towards (首页，上一页，当前页，下一页，尾页) ,
# 用于在 getTowards(),getTowardsDict(),getHtmlId() 函数中选择指定相应页面
towards = ['firstPage','prePage','currentPage','nextPage','lastPage']

# 从文件里提取匹配每一行的url
delEnter = re.compile("http.*")
# 提取脚本中要 innerHTML 部分的 url 
endUrlCmp=re.compile(r'\$\.get\(\"(.*\.htm)')
# 把 innerHTML 的 url 转换成绝对 url
mainHTTP = "http://www.hngp.gov.cn" 

# 存放 page URLs （每页）
SavePagerURLs = "pageUrl.csv"
# 存放 subPage URLs（每条）
SaveSubURLs = "subPageUrl.csv"
# 存放 innerHTML 
SaveInnerPageURLs = "dome.csv"
SaveLogURLs = "log.csv"

htmlparser= "html.parser"
headers= {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	    'Accept-Language':'zh-CN,zh;q=0.8',
		'Cache-Control':'max-age=0',
		'Connection':'keep-alive',
		'Host':'www.hngp.gov.cn',
		'Upgrade-Insecure-Requests':'1',
		'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }

		
logSetURLs=[]  # 记录所有需要重新爬的 URLs 
# 0 -- PageURLs 
# 1 -- SubPageURLs 
# 2 -- InnerHtmlPageURLs
# 3 -- InnerHtmlContent

def SaveLogInFile(log,fname):
	print "the Log File:"
	print len(SaveLogURLs )
	for u in logSetURLs:
		print u
	lfile = open(SaveLogURLs ,"w")
	for i,urlset in enumerate(logSetURLs):
		urls = [j for j in urlset]
		lfile.write("%d"% i)
		for url in urls:
			if url != "":
				lfile.write(",%s" % url)
		lfile.write("\n")
	lfile.close()

# 获取 towards (首页，上一页，当前页，下一页，尾页的) 的 link		
def getTowards(soup,towards):
	for item in soup.find_all("div",class_=re.compile("PageList")):
		for li in item.find_all('li',class_=towards):
			for link in li.find_all('a'):
				return link.get('href') 

# 获取 page URLs  的字典
def getTowardsDict(soup,link_dir):
	global towards
	for twds in towards:
		link_dir[twds]=getTowards(soup,twds)		

# 获取 page URLs  是 几页
def getHtmlId(soup,toward):
	#获取下一页的标号
	url = getTowards(soup,toward)
	cp1 = re.compile(r"pageNo=(\d+)")
	l =cp1.search(url) 
	l=(l.groups(0)[0])
	return l
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
 

# 下载网页到			
def download(url,user_agent=headers,proxy=None,num_retries=5):
    print 'Downloading:',url
    headers = user_agent
    request = urllib2.Request(url,headers=headers)
    opener =urllib2.build_opener()
    if proxy:
        proxy_params = {urlparse.urlparse(url).scheme:proxy}
        opener.add_handler(urllib2.ProxyHandler(proxy_params))
    try:
        html = opener.open(request).read()
    except urllib2.URLError as e:
        print 'Download error:',e.reason
        html = None
        if num_retries > 0:
            if hasattr(e,'code') and 500<=e.code<600:
                html =download(url,user_agent,proxy,num_retries-1)
    return html	


def getLinksFromFile(fname,root=None):
	"""
		注：文件行号从 1 开始 csv 文件格式
		第一个字段 是 文件号，第二个 url
	"""
	bfile = open(fname,"r")
	links= []
	if not bfile:
		print "ERROR: the file %s is not open" % fname
		return links
	#log 处理 失效
	#log = bfile.readline().split(",")
	#if log[0] != 0:
	#	for i in xrange((int)(log[0]),2,-1):
	#		bfile.readline()
	nloop =  1
	while True:
		line = bfile.readline()
		#print line
		if not line:
			break
		#link=line.split(",")
		#
		#if len(link) >1:
		#	link = link[1]
		#	if link != "" and link not in links:
		#		links.append(link)
		#		print link
		link = delEnter.findall(line)[0]
		if link != "" and link not in links:
			links.append(link)
		
		nloop+=1
		if root != None and nloop >= root+1:
			break
	bfile.close()
	return links[:]
	pass

def saveLiksInFile(links,fname,format=None):
	sbfile = open(fname,"w")
	nloop = 0
	if format!=None:
		for url in links:
			sbfile.write("%d,%s%s\n" % (nloop+1,mainHTTP,url[0].encode('utf-8')))
			nloop += 1
	else :
		for url in links:
			sbfile.write("%d,%s\n" % (nloop+1,url))
			nloop += 1
	sbfile.close()
	return nloop
	pass


def getPagerURLs(seed_url,links,root=None):
	global towards
	PageURLset=set()
	if links == [] or (seed_url not in links): 
		#seed_url=setPageSize(seed_url)
		links.append(seed_url)
	nloop = 1
	while True:	
		link = links[-1]
		## 判断 URLs 是否合法
		pass
		## 下载URLs为html，并判断是否成功
		html = download(link,headers)
		if html == None:
			print "ERROR: %s  can't download" % link
			PageURLset.add(link)
			break
		## 生成 BeautiSoup 对象 soup ，并判断是否成功
		soup = BeautifulSoup(html,htmlparser)
		if not soup :
			print "ERROR: %s  can't BeautifulSoup" % link
			PageURLset.add(link)
			break
		## 从 soup 中读取 指定url 存入 urls 中
		nexturl = getTowards(soup,towards[3])
		nexturl = urlparse.urljoin(seed_url,nexturl)
		if not nexturl or nexturl in links:
			break
		else:
			#nexturl =seed_url(nexturl)
			links.append(nexturl)
		nloop += 1
		if root != None and nloop >= root:
			break	
	#getTowards(soup,towards)
	for i in range(len(links)):
		links[i] = setPageSize(links[i])
	# 添加logSetURLs
	if len(logSetURLs) <1 and len(logSetURLs) >=0:
		logSetURLs.append(PageURLsets)
	else:
		logSetURLs[0]=PageURLsets
	pass

def crawlPageURLs(seed_url,SaveFile,root=None):
	urls = []
	try :
		getPagerURLs(seed_url,urls,root=root)
	except Exception as e:
		print e
	finally:
		return saveLiksInFile(urls,SaveFile)

		
# 获取 page URLs  的公告面板的 subPage URLs (绝对路径)
def getSubPageURLs(soup):
	links =[]
	for item in soup.find_all("div",class_="List2"):
		for link in item.find_all('a'):
			links.append(urlparse.urljoin(seed_url,link.get('href')))
			#links.append(link.get('href'))
	return links[:]

def crawSubPageURLs(rfile,wfile,root=None):
	urls = []
	tmpurls = []
	SubPageURLset=set("")
	try:
		links = getLinksFromFile(rfile,root=root)
		#getURLsFromLinks(links,urls,func=getSubPageURLs)
		if True:
			for link in links:
				html = download(link,user_agent=headers)
				if html == None:
					SubPageURLset.add(link)
					continue
				soup = BeautifulSoup(html,htmlparser)
				if soup == None:
					SubPageURLset.add(link)
					continue
				tmpurls = getSubPageURLs(soup)
				for url in tmpurls:
					if url not in  urls:
						urls.append(url)
			for url in tmpurls:
					if url not in  urls:
						urls.append(url)
			pass
	except Exception as e:
		print e
	finally:
		logsize = len(logSetURLs)
		if logsize < 1:
			for i in range(1):
				logSetURLs.append(set())
		else:
			if len(logSetURLs) <2 and len(logSetURLs) >=1:
				logSetURLs.append(SubPageURLset)
			else:
				logSetURLs[1]=PageURLsets
		return saveLiksInFile(urls,wfile)
		

		
def getInnerPageURLs(soup):
	links= []
	for string in soup.stripped_strings:
		dammit = UnicodeDammit(string)
		tmpurl=endUrlCmp.findall(dammit.unicode_markup)
		if tmpurl != [] and tmpurl not in links:
			links.append(tmpurl)
	return links

def crawInnerPageURLs(rfile,wfile,root=None):
	urls =[]
	tmpurl= []
	InnerHtmlPageURLset = set("")
	try:
		links = getLinksFromFile(rfile,root=root)
		#getURLsFromLinks(links,urls,func=getInnerPageURLs)
		if True:
			for link in links:
				html = download(link,user_agent = headers)
				if html == None:
					InnerHtmlPageURLset.add(link)
					continue
				soup = BeautifulSoup(html,htmlparser)
				if soup ==  None:
					InnerHtmlPageURLset.add(link)
					continue
				tmpurl = getInnerPageURLs(soup)
				for url in tmpurl:
					if url not in urls:
						urls.append(url)
			for url in tmpurl:
				if url not in urls:
					urls.append(url)
			pass
	except Exception as e:
		print e
	finally:
		logsize = len( InnerHtmlPageURLset )
		if logsize < 2:
			for i in range(2):
				logSetURLs.append(set(""))
		else:
			if len( InnerHtmlPageURLset ) <3 and len( InnerHtmlPageURLset ) >=2:
				logSetURLs.append( InnerHtmlPageURLset )
			else:
				logSetURLs[2]=PageURLsets
		return saveLiksInFile(urls,wfile,format = 2)

# 从文件 SavePagerURLs 中逐条读取 pagerURL, 并把个 pagerURL 网页中 subURLs 保存到 文件 SaveSubURLs
def saveInnerHTML(dome,root=None):
	dfile=open(dome,"r")
	nloop=1
	InnerHtmlContentset=set("")
	while True:
		line = dfile.readline()
		if not line:
			break
		durl = delEnter.findall(line)[0]
		# 因为格式类似这个[u'/webfile/xinxiang/cgxx/jggg/webinfo/2017/05/1494846022264031.htm'] 
		dhtml = download(durl,headers)
		if dhtml == None:
			InnerHtmlContentset.add(durl)
			break
		soup =BeautifulSoup(dhtml,"html.parser")
		if soup ==None:
			InnerHtmlContentset.add(durl)
			break
		
		saveName = ("inh%s.txt" % nloop)
		saveTxt = open(saveName,"w")
		
		# 调试输出 start #可以保存 innerHTML 的原文件
		#saveName = ("inh%s.html" % nloop)
		#saveHtml =open(saveName,"w")
		#saveHtml.write("%s" % soup.prettify().encode('utf-8'))
		#saveHtml.close()
		# 调试输出  end
		## 读取 stripped_strings 并且 转码
		
		for string in soup.stripped_strings:
			dammit = UnicodeDammit(string)
			# 调试输出
			#print dammit.unicode_markup
			saveTxt.write("%s\n" % dammit.unicode_markup.encode('utf-8'))
		## 关闭 ("%d.txt" % nloop ) 文件
		saveTxt.close()
		# 调试输出  end
		nloop+=1
		if root != None and nloop >= root+1:
			break
	pass
	dfile.close()
	logsize = len(logSetURLs)
	if logsize <3:
		for i in range(3):
			logSetURLs.append(set(""))
	else:
		if len(logSetURLs) <4 and len(logSetURLs) >=3:
				logSetURLs.append(InnerHtmlContentset)
		else:
			logSetURLs[3]=InnerHtmlContentset
	pass
				
if __name__=="__main__":
	# links = []
	# links=getLinksFromFile(SaveSubURLs)
	# print len(links)
	# for i,url in enumerate(links):
	## print "%d,%s" %(i+1,url)
	links = []
	urls = []
	
	seed_url ="http://www.hngp.gov.cn/henan/ggcx?appCode=H60&channelCode=0102"
	#seed_url ="http://www.hngp.gov.cn/henan/ggcx?appCode=H60&channelCode=0102&pageSize=30"
	
	print "It's  module test."
	pi,si,ii,page = 0,0,0,0
	while True:
		chose = raw_input("Please input you chose:\n\ta.Crawl Page URLs\n\tb.Crawl SubPage URLs\n\tc.Crawl InnerPage URLs\n\tq.quit\n\t")
		if chose == "a":
			pi = crawlPageURLs(seed_url,SavePagerURLs)
			print "\ncrawlPageURLs is OK!\nThe file has %d lines \n" % pi
			pass
		elif chose == "b":
			si=crawSubPageURLs(SavePagerURLs,SaveSubURLs)
			print "\ncrawSubPageURLs is OK!The file has %d lines \n" % si
			pass
		elif chose == "c":
			#ii = getSubHtmlContents(SaveSubURLs)
			ii = crawInnerPageURLs(SaveSubURLs,SaveInnerPageURLs) 
			print "\ncrawInnerPageURLs is OK!The file has %d lines \n" % ii
			pass
		elif chose == "q":
			break
			pass
		else:
			pass
	print "\n module test is over,the overlook is :"
	print "%s has %d lines " %(SavePagerURLs,pi)
	print "%s has %d lines " %(SaveSubURLs,si)
	print "%s has %d lines " %(SaveInnerPageURLs,ii)
	
	SaveLogInFile(logSetURLs,SaveLogURLs )
	
	# try ger the innerHtmlContent
	while chose !='y' and chose != 'n' and chose != 'Y' and chose != 'N':
		chose = raw_input("do you want to download the inner html content?(y/n)")
		if chose =='y'  or chose =='Y':
			print "The Inner Html Content" 
			saveInnerHTML(SaveInnerPageURLs)
		pass
	pass
	print "It.s the Whole test:"
	pageInfo = raw_input("Please input how many page you'd like to crawl (zero for all):")
	
	if pageInfo == "0":
	    pi = crawlPageURLs(seed_url,SavePagerURLs)
	else:
		page = int(pageInfo)
		pi = crawlPageURLs(seed_url,SavePagerURLs,root=page)
	
	si=crawSubPageURLs(SavePagerURLs,SaveSubURLs)	
	ii = crawInnerPageURLs(SaveSubURLs,SaveInnerPageURLs)
	print "\n The Page info is %s ,the page is %d" %(pageInfo,page)
	print "\n Whole test is over,the overlook is :"
	print "%s has %d lines " %(SavePagerURLs,pi)
	print "%s has %d lines " %(SaveSubURLs,si)
	print "%s has %d lines " %(SaveInnerPageURLs,ii)
	pass
	while chose !='y' and chose != 'n' and chose != 'Y' and chose != 'N':
		chose = raw_input("do you want to download the inner html content?(y/n)")
		if chose =='y'  or chose =='Y':
			print "The Inner Html Content" 
			saveInnerHTML(SaveInnerPageURLs)
		pass
	SaveLogInFile(logSetURLs,SaveLogURLs )

	
	
	
# 从文件获取URLs
# 保存URLs到??
