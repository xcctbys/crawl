#coding:utf8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import logging
import unittest
import re
from bs4 import BeautifulSoup

DEBUG = True
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")

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

class BaseProxy(object):
    def __init__(self):
        self.url = '' 
        self.timeout = 15
        self.reqst = requests.Session()
        self.reqst.headers.update(
            {'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

    def run(self):
        pass

class XiciProxy(BaseProxy):
    def __init__(self):
        BaseProxy.__init__(self)
        self.url = 'http://www.xicidaili.com/nn'          #西刺代理

    def run(self):
        resp = self.reqst.get(self.url, timeout=self.timeout)
        # trs = BeautifulSoup(resp.content, 'html.parser').find_all('tr')[:60]
        trs = BeautifulSoup(resp.content, 'html.parser').find_all('tr', class_='odd')
        a_list = []
        for tr in trs:
            tds = [td.get_text().strip() for td in tr.find_all('td')]
            try:
                province = choices[tds[3][:2]]
            except KeyError:
                province = 'OTHER'
            http =  "%s:%s" % (tds[1],tds[2])
            http = (http, province)
            # print http
            a_list.append(http)
        # print '-----------------xici_proxy_list--------------------'
        # print a_list
        return a_list

class HaoProxy(BaseProxy):
    def __init__(self):
        BaseProxy.__init__(self)
        self.url = 'http://www.haodailiip.com/guonei/'          #好代理

    def run(self):
        hao_proxy_list = []
        for i in range(1,3):
            resp = self.reqst.get(self.url+str(i), timeout=self.timeout)
            trs = BeautifulSoup(resp.content, 'html.parser').find_all('tr')[5:]
            for tr in trs:
                tds = [td.get_text().strip() for td in tr.find_all('td')]
                try:
                    province = choices[tds[2][:2]]
                except KeyError:
                    province = 'OTHER'
                http = "%s:%s" % (tds[0], tds[1])
                http = (http, province)
                hao_proxy_list.append(http)
        # print '-----------------hao_proxy_list--------------------'
        # print hao_proxy_list
        return hao_proxy_list

class KuaiProxy(BaseProxy):
    def __init__(self):
        BaseProxy.__init__(self)
        self.url = 'http://www.kuaidaili.com/free/inha/'          #快代理

    def run(self):
        pass
        #####为什么总是 http 521的状态码？该问题还没有解决
        # kuai_proxy_list = []
        # for i in range(1,3):
        #     resp = self.reqst.get('http://www.kuaidaili.com/')
        #     resp = self.reqst.get(self.url+str(i), timeout=self.timeout)
        #     print resp.status_code
        #     trs = BeautifulSoup(resp.content, 'html.parser').find_all('tr')[1:]
        #     for tr in trs:
        #         tds = [td.get_text().strip() for td in tr.find_all('td')]
        #         try:
        #             province = choices[tds[4][:2]]
        #         except Exception as e:
        #             province = 'OTHER'
        #         http = "%s:%s" % (tds[0], tds[1])
        #         http = (http, province)
        #         kuai_proxy_list.append(http)
        # print '-----------------kuai_proxy_list--------------------'
        # print kuai_proxy_list
        # return kuai_proxy_list

class YouProxy(BaseProxy):
    def __init__(self):
        BaseProxy.__init__(self)
        self.url = 'http://www.youdaili.net/Daili/guonei/'          #有代理

    def run(self):
        resp = self.reqst.get(self.url, timeout=self.timeout)
        ul = BeautifulSoup(resp.content, 'html.parser').find_all('ul', attrs={'class':'newslist_line'})[0]
        try:
            a_href = ul.find('li').a['href']
            resp = self.reqst.get(a_href, timeout=self.timeout)
            content = BeautifulSoup(resp.content, 'html.parser').find_all('p')[0]
            you_proxy_list = []
            for item in content.span.get_text().split()[::2]:
                try:
                    ip_port, province = item.split('@')
                    province = province.split('#')[1]
                    if province[0] == u'【':
                        province = choices[province[3:6]]
                    else:
                        province = choices[province[:2]]
                except ValueError:
                    pass
                except KeyError:
                    province = 'OTHER'
                you_proxy_list.append((ip_port, province))
            return you_proxy_list
            # for item in content.span.get_text().split('\n'):
            #     print item.get_text().strip()

        except Exception as e:
            return None

class SixProxy(BaseProxy):
    def __init__(self):
        BaseProxy.__init__(self)
        self.url = 'http://www.66ip.cn/areaindex_'          #66代理

    def run(self):
        a_list = []
        for i in range(1,33):
            url = self.url+str(i)+'/'+'1.html'
            try:
                resp = self.reqst.get(url, timeout=self.timeout)
            except:
                continue
            table = BeautifulSoup(resp.content, 'html.parser').find_all('table', attrs={'width':'100%', 'border':"2px", 'cellspacing':"0px", 'bordercolor':"#6699ff"})[0]
            trs = table.find_all('tr')[1:6]
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
        # print '-------------six_proxy_list-------------------'
        # print a_list
        return a_list

class IPCNProxy(BaseProxy):
    def __init__(self):
        BaseProxy.__init__(self)
        self.url = 'http://proxy.ipcn.org/country/'          #IPCN代理
        self.url2 = 'http://proxy.ipcn.org/proxylist.html'

    def run(self):
        resp = self.reqst.get(self.url, timeout=self.timeout)
        table = BeautifulSoup(resp.content, 'html.parser').find_all('table', attrs={'border':'1', 'size':'85%'})[-1]
        # print [td.get_text().strip() for td in table.find_all('td')[:40]]
        proxy_list1 = [(td.get_text().strip(), 'OTHER') for td in table.find_all('td')[:50] if td and td.get_text().strip()]
        resp = self.reqst.get(self.url2, timeout=self.timeout)
        table = BeautifulSoup(resp.content, 'html.parser').find_all('pre')[-1]
        proxy_list2 = [(item.strip(), 'OTHER') for item in table.get_text().split('\n')[6:-2]]
        proxy_list2.extend(proxy_list1)
        # print '-------------ipcn_proxy_list----------------'
        # print proxy_list2
        return proxy_list2

class NovaProxy(BaseProxy):
    def __init__(self):
        BaseProxy.__init__(self)
        self.url = 'http://www.proxynova.com/proxy-server-list/country-cn/'

    def run(self):
        resp = self.reqst.get(self.url, timeout=self.timeout)
        table = BeautifulSoup(resp.content, 'html.parser').find('table', id='tbl_proxy_list').find('tbody').find_all('tr')
        proxy_list = []
        for proxy in table:
            try:
                p = proxy.find_all('td')
                ip = p[0].get_text().strip()
                
                pattern =re.compile("(\d*\.\d*\.\d*\.\d*)")
                ipre = pattern.search(ip)
                ip = ipre.group   
                
                port = p[1].get_text().strip()
                province = 'OTHER' #p[5].get_text().strip()
                # anony = p[6].get_text().strip()
                proxy_list.append((ip+ ':' +port, province))
            except Exception:
                pass
        # print proxy_list
        return proxy_list

class Ip84Proxy(BaseProxy):
    def __init__(self):
        BaseProxy.__init__(self)
        self.url = 'http://ip84.com/dlgn-http'

    def run(self):
        resp = self.reqst.get(self.url, timeout=self.timeout)
        table = BeautifulSoup(resp.content, 'lxml').find('table', attrs={'class':'list'}).find_all('tr')[1:]
        proxy_list = []
        for tr in table:
            p = [td.get_text() for td in tr.select('td')]
            ip_port = ':'.join(p[:2])
            try:
                province = choices[p[2].strip()]
            except KeyError:
                province = 'OTHER'
            proxy_list.append((ip_port, province))
        return proxy_list







class ProxyTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_obtain_xici_proxy_list(self):
        self.xici = XiciProxy()
        xici_proxy_list = self.xici.run()
        self.assertTrue(xici_proxy_list)
        # print '-----------xici_proxy_list------------------'
        # for item in xici_proxy_list:
            # print item
        logging.debug('xici_proxy_list: %s ' % xici_proxy_list)

    def test_obtain_six_proxy_list(self):
        self.six = SixProxy()
        six_proxy_list = self.six.run()
        self.assertTrue(six_proxy_list)
        # print '-----------six_proxy_list------------------'
        # for item in six_proxy_list:
            # print item
        logging.debug('six_proxy_list:%s' % six_proxy_list )

    def test_obtain_ipcn_proxy_list(self):
        self.ipcn = IPCNProxy()
        ipcn_proxy_list = self.ipcn.run()
        self.assertTrue(ipcn_proxy_list)
        # print '-----------ipcn_proxy_list------------------'
        # for item in ipcn_proxy_list:
            # print item
        logging.debug('ipcn_proxy_list: %s' % ipcn_proxy_list)

    def test_obtain_hao_proxy_list(self):
        self.hao = HaoProxy()
        hao_proxy_list = self.hao.run()
        self.assertTrue(hao_proxy_list)
        # print '-----------hao_proxy_list------------------'
        logging.debug('hao_proxy_list: %s ' % hao_proxy_list)

    def test_obtain_kuai_proxy_list(self):
        self.kuai = KuaiProxy()
        kuai_proxy_list = self.kuai.run()
        self.assertTrue(not kuai_proxy_list)
        logging.debug('kuai_proxy_list: %s ' % kuai_proxy_list)

    def test_obtain_you_proxy_list(self):
        self.you = YouProxy()
        you_proxy_list = self.you.run()
        self.assertTrue(you_proxy_list)
        logging.debug('you_proxy_list: %s ' % you_proxy_list)

    def test_obtain_nova_proxy_list(self):
        self.nova = NovaProxy()
        nova_proxy_list = self.nova.run()
        self.assertTrue(nova_proxy_list)
        logging.debug('nova_proxy_list: %s ' % nova_proxy_list)
    
    def test_obtain_ip84_proxy_list(self):
        self.ip84 = Ip84Proxy()
        ip84_proxy_list = self.ip84.run()
        self.assertTrue(ip84_proxy_list)
        logging.debug('ip84_proxy_list: %s ' % ip84_proxy_list)

if __name__ == '__main__':
    
    if DEBUG:
        unittest.main()
    """
    test =ProxyTest()
    test.test_obtain_nova_proxy_list()
    """
