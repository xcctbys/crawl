#coding:utf8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
from bs4 import BeautifulSoup

choices = dict([
(u'安徽', 'ANHUI'),
(u'北京', 'BEIJING'),
(u'重庆', 'CHONGQING'),
(u'福建', 'FUJIAN'),
(u'甘肃', 'GANSU'),
(u'广东', 'GUANGDONG'),
(u'广西', 'GUANGXI'),
(u'贵州', 'GUIZHOU'),
(u'海南', 'HAINAN'),
(u'河北', 'HEBEI'),
(u'黑龙', 'HEILONGJIANG'),
(u'河南', 'HENAN'),
(u'湖北', 'HUBEI'),
(u'湖南', 'HUNAN'),
(u'江苏', 'JIANGSU'),
(u'江西', 'JIANGXI'),
(u'吉林', 'JILIN'),
(u'辽宁', 'LIAONING'),
(u'内蒙', 'NEIMENGGU'),
(u'宁夏', 'NINGXIA'),
(u'青海', 'QINGHAI'),
(u'陕西', 'SHAANXI'),
(u'山东', 'SHANDONG'),
(u'上海', 'SHANGHAI'),
(u'山西', 'SHANXI'),
(u'四川', 'SICHUAN'),
(u'天津', 'TIANJIN'),
(u'新疆', 'XINJIANG'),
(u'云南', 'YUNNAN'),
(u'浙江', 'ZHEJIANG'),
(u'总局', 'ZONGJU'),
(u'西藏', 'XIZANG')])

class Xici(object):
    def __init__(self):
        self.url = 'http://www.xicidaili.com/nn'          #西刺代理
        self.reqst = requests.Session()
        self.reqst.headers.update(
            {'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

    def run(self):
        resp = self.reqst.get(self.url, timeout=60)
        trs = BeautifulSoup(resp.content, 'html.parser').find_all('tr')[:50]
        a_list = []
        for tr in trs[2:]:
            tds = [td.get_text().strip() for td in tr.find_all('td')]
            try:
                province = choices[tds[4][:2]]
            except:
                province = 'OTHER'
            http =  "%s:%s" % (tds[2],tds[3])
            http = (http, province)
            # print http
            a_list.append(http)
        # print a_list
        return a_list

class HaoProxy(Xici):
    def __init__(self):
        super(Xici, self).__init__()
        self.url = 'http://www.xicidaili.com/nn'          #西刺代理
    def run(self):
        pass

class KuaiProxy(Xici):
    def __init__(self):
        super(Xici, self).__init__()
        self.url = 'http://www.xicidaili.com/nn'          #西刺代理
    def run(self):
        pass

class YouProxy(Xici):
    def __init__(self):
        super(Xici, self).__init__()
        self.url = 'http://www.xicidaili.com/nn'          #西刺代理
    def run(self):
        pass

class SixProxy(Xici):
    def __init__(self):
        self.reqst = requests.Session()
        self.reqst.headers.update(
            {'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})
        self.url = 'http://www.66ip.cn/areaindex_'          #西刺代理
    def run(self):
        a_list = []
        for i in range(1,33):
            url = self.url+str(i)+'/'+'1.html'
            try:
                resp = self.reqst.get(url, timeout=30)
            except:
                continue
            table = BeautifulSoup(resp.content, 'html.parser').find_all('table', attrs={'width':'100%', 'border':"2px", 'cellspacing':"0px", 'bordercolor':"#6699ff"})[0]
            trs = table.find_all('tr')[1:4]
            for tr in trs:
                tds = [td.get_text().strip() for td in tr.find_all('td') if td.get_text()]
                http = "%s:%s" % (tds[0],tds[1])
                try:
                    province = choices[tds[2][:2]]
                except:
                    province = 'OTHER'
                # print 'http:------------',http
                if http:
                    a_list.append((http, province))
        # print a_list
        return a_list

class IPCNProxy(Xici):
    def __init__(self):
        # super(Xici, self).__init__()
        self.reqst = requests.Session()
        self.reqst.headers.update(
            {'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})
        self.url = 'http://proxy.ipcn.org/country/'          #IPCN代理
    def run(self):
        resp = self.reqst.get(self.url, timeout=10)
        table = BeautifulSoup(resp.content, 'html.parser').find_all('table', attrs={'border':'1', 'size':'85%'})[-1]
        # print [td.get_text().strip() for td in table.find_all('td')[:40]]
        return [(td.get_text().strip(), 'OTHER') for td in table.find_all('td')[:50] if td and td.get_text().strip()]

if __name__ == '__main__':
    xici = Xici()
    xici.run()