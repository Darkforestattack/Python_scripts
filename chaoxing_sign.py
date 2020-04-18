import requests,json,time

#获取Cookie和UID
username = ''  # 超星账号
password = ''  # 超星密码
a = ""
headers = {
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 ChaoXingStudy/ChaoXingStudy_3_4.3.2_ios_phone_201911291130_27 (@Kalimdor)_11391565702936108810"
}
url = 'http://passport2.chaoxing.com/api/login?name={}&pwd={}&schoolid=&verify=0'.format(username, password)
re = requests.get(url, headers=headers)
asd = requests.utils.dict_from_cookiejar(re.cookies)
for i in asd:
    a = a + i +' = '+ asd.get(i) + ";"
a = str(a)
UID = asd.get('UID')
UID = str(UID)

#填入Cookie
headers={
  "Cookie": a,
  "User-Agent": "Mozilla/5.0 (iPad; CPU OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 ChaoXingStudy/ChaoXingStudy_3_4.3.2_ios_phone_201911291130_27 (@Kalimdor)_11391565702936108810"
}
#填入uid
uid = UID
coursedata=[]
activeList=[]
course_index=0
speed=10
status=0
status2=0
activates=[]
def backclazzdata():
    global coursedata
    url="http://mooc1-api.chaoxing.com/mycourse/backclazzdata?view=json&rss=1"
    res=requests.get(url,headers=headers)
    cdata=json.loads(res.text)
    if(cdata['result']!=1):
        print("课程列表获取失败")
        return 0
    for item in cdata['channelList']:
        if("course" not in item['content']):
            continue
        pushdata={}
        pushdata['courseid']=item['content']['course']['data'][0]['id']
        pushdata['name']=item['content']['course']['data'][0]['name']
        #pushdata['imageurl']=item['content']['course']['data'][0]['imageurl']
        pushdata['classid']=item['content']['id']
        coursedata.append(pushdata)
    print("课程列表获取成功")  
    #print(coursedata)  
    printdata()

def printdata():
    global course_index,speed
    index=1
    for item in coursedata:
        print(str(index)+".课程名称:"+item['name'])
        index+=1
    course_index=int(input("请输入序号以设定监控课程"))-1
    print("监控课程设定完成")
    speed=int(input("请输入监控频率"))
    print("监控频率设置完毕")
    res=input("输入start启动监控")
    if(res=="start"):
        startsign()
    else:
        printdata    



def taskactivelist(courseId,classId):
    global activeList
    url="https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist?courseId="+str(courseId)+"&classId="+str(classId)+"&uid="+uid
    res=requests.get(url,headers=headers)
    data=json.loads(res.text)
    activeList=data['activeList']
    #print(activeList)
    for item in activeList:
        if("nameTwo" not in item):
            continue
        if(item['activeType']==2 and item['status']==1):
            signurl=item['url']
            aid = getvar(signurl)
            if(aid not in activates):
                print("【签到】查询到待签到活动 活动名称:%s 活动状态:%s 活动时间:%s aid:%s"%(item['nameOne'],item['nameTwo'],item['nameFour'],aid))
                sign(aid,uid)   

def getvar(url):
    var1 = url.split("&")
    for var in var1:
        var2 = var.split("=")
        if(var2[0]=="activePrimaryId"):
            return var2[1]
    return "ccc"    

  

def sign(aid,uid):
    global status,activates
    url="https://mobilelearn.chaoxing.com/pptSign/stuSignajax?activeId="+aid+"&uid="+uid+"&clientip=&latitude=-1&longitude=-1&appType=15&fid=0"
    res=requests.get(url,headers=headers)
    if(res.text=="success"):
        print("用户:"+uid+" 签到成功！")
        activates.append(aid)
        status=2
    else:
        print("签到失败")  
        activates.append(aid)  

def startsign():
    global status,status2
    status=1
    status2=1
    ind=1
    print("监控启动 监控课程为:%s 监控频率为:%s"%(coursedata[course_index]['name'],str(speed)))
    while(status!=0 and status2!=0):
        ind+=1
        taskactivelist(coursedata[course_index]['courseid'],coursedata[course_index]['classid'])
        time.sleep(speed)
        if(status==1):
            print(str(ind)+" [签到]监控课程运行中，未查询到签到活动")
        elif(status==2):
            print(str(ind)+" [新签到]监控运行中，未查询到签到活动")         
    print("任务结束")
    printdata()

backclazzdata()
