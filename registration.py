# -*- coding: utf-8 -*-
# author: stone


from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException,NoAlertPresentException
import time
from twilio.rest import Client

# 用于发送短信验证是否登记成功
account_sid = "xxxxxxxxxxxxx"       #twilio网站给的sid
auth_token = "**************"       #twilio网站给的token
Client = Client(account_sid,auth_token)
time_now = str(time.strftime('%Y年%m月%d日',time.localtime(time.time())))

# 登陆信息
username = "xxxxxxxxxx"           # 学号
password = "xxxxxxxxxx"                 # 密码
urls = ["url1","url2","url3","url4"]        #网站近期增加了服务器

# 设置浏览器
browser = webdriver.Edge()
browser.implicitly_wait(5)

def regis(username,password,urls):
    web_condition(urls)
    # 输入账号
    browser.find_element_by_id("username").click()
    browser.find_element_by_id("username").send_keys(username)

    # 输入密码
    browser.find_element_by_id("userpwd").click()
    browser.find_element_by_id("userpwd").send_keys(password)

    # 获取验证码
    code = browser.find_elements_by_tag_name("div")[14].text[2:6]

    # 输入验证码
    browser.find_element_by_id("code").click()
    browser.find_element_by_id("code").send_keys(code)

    # 登陆
    browser.find_element_by_id("提交").click()

    # 页面跳转处理
    handles = browser.window_handles
    for handle in handles:
        #先切换到该窗口
        browser.switch_to.window(handle)
        # 得到该窗口的标题栏字符串，判断是不是我们要操作的那个窗口
        if "管理系统" in browser.title:
            # 如果是，那么这时候WebDriver对象就是对应的该该窗口，跳出循环
            break
    print("窗口切换成功")

    # 获取疫情信息登记界面地址
    browser.switch_to.frame('leftFrame')
    link = browser.find_element_by_xpath("/html/body/div/div/div[5]/ul[7]/li[2]/a")
    herf = str(link.get_attribute('href'))

    #进入疫情登记页面
    browser.get(herf)

    # 一键登记
    browser.find_element_by_xpath('//input[@value="【一键登记：无变化】"]').click()
    time.sleep(5)

    # 检测登记是否成功
    regis_test()

# 检测网络节点状况
def web_condition(urls):
    def condition(urls):
        n = 0
        browser.get(urls[0])
        web = browser.find_elements_by_tag_name('img')[0].get_attribute('src')
        while "poor.png" in web:
            n += 1
            print('%d号站点网络堵塞'%(n))
            browser.get(urls[n])
            web = browser.find_elements_by_tag_name('img')[0].get_attribute('src')
        else:
            print("%d号站点通畅"%(n))
    try:
        condition(urls)
    except UnexpectedAlertPresentException:
        browser.switch_to.alert.accept()
        condition(urls)
    except NoAlertPresentException:
        condition(urls)
    

# 检测是否登记成功&发送登记成功短信&退出
def regis_test():
    alert_text = str(browser.switch_to.alert.text)
    print(alert_text)
    if "登记已存在" or "提交成功" in alert_text:
        # 向手机发送登记成功短信
        message = Client.messages.create(
            to = "+8618728580701",
            from_="+12055128978",
            body = "%s登记成功"%time_now
        )
        # 关闭alert窗口
        dig_alert = browser.switch_to.alert
        dig_alert.accept()
        # 退出系统&关闭浏览器
        browser.get("url_logout")       #退出签到系统
        browser.quit()
        print("登记成功")
    else:
        regis(username,password,urls)

regis(username,password,urls)
