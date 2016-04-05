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
            http =  "%s:%s,%s" % (tds[2],tds[3], province)
            print http
            a_list.append(http)
        # print a_list
        return a_list

if __name__ == '__main__':
    xici = Xici()
    xici.run()