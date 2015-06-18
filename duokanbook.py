#-*- coding:utf-8 -*-

import requests
import re
import sqlite3
import datetime

#本程序用于每日抓取多看计算机类图书价格并保存在数据库中，同时与昨日该书价格对比，如果价格下降则输出提示。

dict = {}
#获取今日日期
ISOFORMAT='%Y%m%d'
tod = datetime.date.today()
today = tod.strftime(ISOFORMAT)

#获取昨日日期
yesterd = tod - datetime.timedelta(days=1)
yesterday = yesterd.strftime(ISOFORMAT)

#创建今日新表
conn = sqlite3.connect('duokan.db')
cursor = conn.cursor()
cursor.execute("DROP TABLE '%s'"%(today))
#cursor.execute("CREATE TABLE '%s'(name VARCHAR,price VARCHAR)"%(yesterday))
cursor.execute("CREATE TABLE '%s'(name VARCHAR,price VARCHAR)"%(today))
conn.commit()
cursor.close()


#获得昨日dict
def get_dict():
    cursor = conn.cursor()
    yespri = cursor.execute("SELECT * FROM '%s'"%(yesterday))
    yesprice = cursor.fetchall()
    #表转换为dict
    for yespri in yesprice:
        dict[yespri[0]] = yespri[1]
    conn.commit()
    cursor.close()
    #print dict
    return dict

#比较今日和昨日的价格
def checkprice(lis):
    for bknameprice in lis:
        bknm= bknameprice[0]
        bkpi= bknameprice[1]
        try:
            if str(bkpi) < str(dict[bknm]):
                print bknm+" Price："+dict[bknm]+" ---> "+bkpi
            else:
                continue
        except:
            print "Newbook: "+bknm+" Price: "+bkpi+" RMB"


#将获取的书名和当前价格存入新表
def pricode(lis):
    for bknameprice in lis:
        bknm= bknameprice[0]
        bkpi= bknameprice[1]
        cursor = conn.cursor()
        cursor.execute("INSERT INTO '%s' VALUES('%s','%s')"%(today,bknm,bkpi))
        conn.commit()
        cursor.close()



#获取总页数
pageget = requests.get('http://www.duokan.com/list/6-1-1')
allnum = re.findall(r'6-1-(\d{1,3})',pageget.text)
allsort = sorted(allnum)
print ("共获取页数："+str(allsort[-1]))
dict = get_dict()

#循环获取所有页面的书名和当前价格
page = int(allsort[-1])
for pagenum in range(page,-1,-1):
    #print pagenum
    try:
        dkcompuhtml = requests.get('http://www.duokan.com/list/6-1-'+str(pagenum),timeout=100)
        dkb = dkcompuhtml.text
        bookname = re.findall(r'alt=\"(.{1,100}?)\" ondragstart.*?\<em\>.{,10}?(\d{,3}\.\d{2})',dkb,re.S)
        
        pricode(bookname)
        checkprice(bookname)
    except:
        continue
conn.close()


