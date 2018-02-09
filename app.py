'''

@author: 王震 西安工程大学

@license: MIT

@contact: 1341046884@qq.com

@file: app.py

@time: 2018/2/9 10:35

'''

from lxml import etree
from flask import Flask, request, render_template
import requests
import re
from bs4 import BeautifulSoup
from gevent import monkey
monkey.patch_all()
app = Flask(__name__)
def getVIEW(Page):  # Get viewststes for login page
    """

    :param Page:
    :return:
    """
    view = r'name="__VIEWSTATE" value="(.+)" '
    view = re.compile(view)
    return view.findall(Page)
def getGrade(response):
    html = response.content
    soup = BeautifulSoup(html.decode("gbk"), "html5lib")
    trs = soup.find(id="Datagrid1").findAll("tr")[1:]
    Grades = []
    for tr in trs:
        tds = tr.findAll("td")
        tds = tds[:2] + tds[3:5] + tds[6:9]
        oneGradeKeys = ["year", "term", "name", "type", "credit", "gradePonit", "grade"]
        oneGradeValues = []
        for td in tds:
            oneGradeValues.append(td.string)
        oneGrade = dict((key, value) for key, value in zip(oneGradeKeys, oneGradeValues))
        Grades.append(oneGrade)
    return Grades
header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': '202.200.206.54',
    'Referer': 'http://202.200.206.54/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.8 Safari/537.36',
}
url = 'http://202.200.206.54/'
@app.route('/')
def index():
    login_url = requests.get(url).url
    base_url = login_url[:49]
    authcode_url = base_url + "CheckCode.aspx?"
    return render_template('index.html',login_url=login_url,imgurl=authcode_url)

@app.route('/login', methods=['POST'])
def login():
    if request.method == "POST":
        try:
            username = request.form.get('num')#学号
            password = request.form.get('pasd')#密码
            login_url = request.form.get('login_url')#登录地址
            yzm= request.form.get('yzm')#验证码
            s = requests.Session()
            value="dDwxODEzMTcwMTU1Ozs+SEh/a3A6kLLAdK5razSinyLKsbE="
            base_url = login_url[:49]
            postdata = {
                'txtUserName': username,
                'TextBox2': password,
                'RadioButtonList1': '学生',
                'Button1': '',
                'lbLanguage': '',
                'hidPdrs': '',
                'hidsc': '',
                '__VIEWSTATE': value,
                "txtSecretCode": yzm
            }
            s.post(login_url, data=postdata, headers=header)  # 登录
            # 获取姓名
            r = s.get(base_url + 'xs_main.aspx?xh=' + username)
            r.encoding = 'gbk'
            content = r.content.decode('gb2312')  # 网页源码是gb2312要先解码
            selector = etree.HTML(content)
            text = selector.xpath('//*[@id="xhxm"]/text()')[0]
            text = text.replace(" ", "")
            studentname = text[:10]
            studentname = studentname[:len(studentname) - 2]
            #查询历年成绩
            url = base_url + "xscjcx.aspx?xh=" + str(username) + "&xm=" + studentname + "&gnmkdm=N121623"
            response = s.get(url, headers=header)
            __VIEWSTATE = getVIEW(response.text)
            postdata2 = {
                "__VIEWSTATE": __VIEWSTATE,
                "btn_zcj": "历年成绩",
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "",
                'hidLanguage': "",
                "ddlXN": "",
                "ddlXQ": "",
                "ddl_kcxz": "",
            }
            r = s.post(url=base_url + "xscjcx.aspx?xh=" + str(username) + "&xm=" + studentname + "&gnmkdm=N121623",
                       data=postdata2,
                       headers=header)
            gre = getGrade(r)
            s.close()
            return render_template('main.html',name=studentname ,gres=gre)
        except:
            return render_template('404.html')
    else:
        return "<h1>login Failure !</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
