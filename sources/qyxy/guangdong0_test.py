#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import unittest
from Guangdong0 import Guangdong0


# urls ={
#         "main": "http://www.szcredit.com.cn/web/GSZJGSPT/QyxyDetail.aspx?rid=4a7c1ee86a544933abed6b502735ad08",
#         "ind_comm_url" : "http://www.szcredit.com.cn/web/GSZJGSPT/QyxyDetail.aspx?rid=4a7c1ee86a544933abed6b502735ad08",
#         "ent_pub_url" : "http://www.szcredit.com.cn/web/GSZJGSPT/QynbDetail.aspx?rid=4a7c1ee86a544933abed6b502735ad08",
#         "other_dept_pub_url": "http://www.szcredit.com.cn/web/GSZJGSPT/QtbmDetail.aspx?rid=4a7c1ee86a544933abed6b502735ad08",
#         # "judical_assist_url": "http://gsxt.gdgs.gov.cn/aiccips/judiciaryAssist/judiciaryAssistInit.html",
#         }
urls ={
"main": "http://www.szcredit.com.cn/web/GSZJGSPT/QyxyDetail.aspx?rid=9c245e77c5d8445e85b3915adb317857",
"ind_comm_url" :"http://www.szcredit.com.cn/web/GSZJGSPT/QyxyDetail.aspx?rid=9c245e77c5d8445e85b3915adb317857",
"ent_pub_url" : "http://www.szcredit.com.cn/web/GSZJGSPT/QynbDetail.aspx?rid=9c245e77c5d8445e85b3915adb317857",
"other_dept_pub_url" : "http://www.szcredit.com.cn/web/GSZJGSPT/QtbmDetail.aspx?rid=9c245e77c5d8445e85b3915adb317857"
}
class TestGuangdong0(unittest.TestCase):
    def setUp(self):
        self.guangdong = Guangdong0()

        self.crawler = self.guangdong.crawler
        self.analyser = self.guangdong.analysis

    def tearDown(self):
        self.guangdong = None

class TestMain(TestGuangdong0):

    def test_run_crawl_ind_comm_pub_pages(self):
        data = self.crawler.crawl_ind_comm_pub_pages(urls['ind_comm_url'])
        print data
        self.assertIsNotNone(data)

    def test_run_crawl_ent_pub_pages(self):
        data = self.crawler.crawl_ent_pub_pages(urls['ent_pub_url'])
        print data
        self.assertIsNotNone(data)

    def test_run_crawl_other_dept_pub_pages(self):
        data = self.crawler.crawl_other_dept_pub_pages(urls['other_dept_pub_url'])
        print data
        self.assertIsNotNone(data)

    @unittest.skip("skip judical assist pub page")
    def test_run_crawl_judical_assist_pub_pages(self):
        pass

class IndCommPubPages(TestGuangdong0):
    def setUp(self):
        TestGuangdong0.setUp(self)
        self.url = urls['ind_comm_url']
        self.page = self.crawler.crawl_page_by_url(self.url)['page']

    def test_table_download_page(self):
        self.assertIsNotNone(self.page)
    # @unittest.skip("demonstrating skipping")
    def test_table_download_page_xingzhengchufa(self):
        self.page_xingzhengchufa = self.crawler.crawl_xingzhengchufa_page(self.url, self.page)
        self.assertIsNotNone(self.page_xingzhengchufa)
    # @unittest.skip("bian geng xin xi page")
    def test_table_download_page_biangengxinxi(self):
        self.page_xingzhengchufa = self.crawler.crawl_xingzhengchufa_page(self.url, self.page)
        self.page_biangengxinxi = self.crawler.crawl_biangengxinxi_page(self.url, self.page_xingzhengchufa)
        self.assertIsNotNone(self.page_biangengxinxi)

    def test_table_basic_investor(self):
        dict_jiben = self.analyser.parse_page(self.page, 'jibenxinxi')
        self.assertTrue(dict_jiben.has_key(u'投资人信息'))
        self.assertIsNotNone(dict_jiben[u'投资人信息'])

    def test_table_basic_info(self):
        dict_jiben = self.analyser.parse_page(self.page, 'jibenxinxi')
        self.assertTrue(dict_jiben.has_key(u'基本信息'))
        self.assertIsNotNone(dict_jiben[u'基本信息'])

    def test_table_change_info(self):
        self.page_xingzhengchufa = self.crawler.crawl_xingzhengchufa_page(self.url, self.page)
        self.page_biangengxinxi = self.crawler.crawl_biangengxinxi_page(self.url, self.page_xingzhengchufa)
        bg = self.analyser.parse_page(self.page_biangengxinxi, 'biangengxinxi')
        self.assertTrue(bg.has_key(u'变更信息'))
        self.assertIsNotNone(bg[u'变更信息'])

    def test_table_beian_person(self):
        dict_jiben = self.analyser.parse_page(self.page, 'beian')
        self.assertTrue(dict_jiben.has_key(u'主要人员信息'))
        self.assertIsNotNone(dict_jiben[u'主要人员信息'])
    def test_table_beian_branch(self):
        dict_jiben = self.analyser.parse_page(self.page, 'beian')
        self.assertTrue(dict_jiben.has_key(u'分支机构信息'))
        self.assertIsNotNone(dict_jiben[u'分支机构信息'])
    def test_table_beian_clear(self):
        dict_jiben = self.analyser.parse_page(self.page, 'beian')
        self.assertTrue(dict_jiben.has_key(u'清算信息'))
        # with self.assertRaises(KeyError):
        #     value = dict_jiben[u'清算信息']
        self.assertIsNotNone(dict_jiben[u'清算信息'])

    def test_table_equity_ownership(self):
        dict_jiben = self.analyser.parse_page(self.page, 'guquanchuzi')
        self.assertTrue(dict_jiben.has_key(u'股权出质登记信息'))
        self.assertIsNotNone(dict_jiben[u'股权出质登记信息'])

    def test_table_movable_property(self):
        dict_jiben = self.analyser.parse_page(self.page, 'dongchandiya')
        self.assertTrue(dict_jiben.has_key(u'动产抵押登记信息'))
        self.assertIsNotNone(dict_jiben[u'动产抵押登记信息'])

    def test_table_administration_sanction(self):
        self.page_xingzhengchufa = self.crawler.crawl_xingzhengchufa_page(self.url, self.page)
        dict_jiben = self.analyser.parse_page(self.page_xingzhengchufa, 'xingzhengchufa')
        self.assertTrue(dict_jiben.has_key(u'行政处罚信息'))
        self.assertIsNotNone(dict_jiben[u'行政处罚信息'])

    def test_table_business_exception(self):
        dict_jiben = self.analyser.parse_page(self.page, 'jingyingyichang')
        self.assertTrue(dict_jiben.has_key(u'异常名录信息'))
        self.assertIsNotNone(dict_jiben[u'异常名录信息'])

    def test_table_violate_law(self):
        dict_jiben = self.analyser.parse_page(self.page, 'yanzhongweifa')
        self.assertTrue(dict_jiben.has_key(u'严重违法信息'))
        self.assertIsNotNone(dict_jiben[u'严重违法信息'])

    def test_table_spot_check(self):

        dict_jiben = self.analyser.parse_page(self.page, 'chouchajiancha')
        self.assertTrue(dict_jiben.has_key(u'抽查检查信息'))
        self.assertIsNotNone(dict_jiben[u'抽查检查信息'])

class EntPubPages(TestGuangdong0):

    def setUp(self):
        TestGuangdong0.setUp(self)
        self.url = urls['ent_pub_url']
        self.page = self.crawler.crawl_page_by_url(self.url)['page']
    @unittest.skip("annual table test")
    def test_table_annual_report_function(self):
        aurl = "http://www.szcredit.com.cn/web/GSZJGSPT/NBGSDetai.aspx?Entid=440301001012012102503211&NBYear=2014"
        result = self.crawler.crawl_page_by_url(aurl)
        self.assertIsNotNone(result['page'])
        self.assertIsNotNone(result['url'])
        data = self.analyser.parse_ent_pub_annual_report_page(result, "_detail")
        self.assertIsNotNone(data)

    # @unittest.skip("annual report")
    def test_table_annual_report(self):
        dict_jiben = self.analyser.parse_page(self.page, 'qiyenianbao')
        self.assertTrue(dict_jiben.has_key(u'企业年报'))
        self.assertIsNotNone(dict_jiben[u'企业年报'])

    # @unittest.skip("annual report")
    def test_table_permission(self):
        dict_jiben = self.analyser.parse_page(self.page, 'xingzhengxuke')
        self.assertTrue(dict_jiben.has_key(u'行政许可信息'))
        self.assertIsNotNone(dict_jiben[u'行政许可信息'])
    # @unittest.skip("annual report")
    def test_table_sanction(self):
        dict_jiben = self.analyser.parse_page(self.page, 'xingzhengchufa')
        self.assertTrue(dict_jiben.has_key(u'行政处罚信息'))
        self.assertIsNotNone(dict_jiben[u'行政处罚信息'])
    # @unittest.skip("annual report")
    def test_table_shareholder_capital(self):
        dict_jiben = self.analyser.parse_page(self.page, 'touziren')
        self.assertTrue(dict_jiben.has_key(u'股东及出资信息'))
        self.assertIsNotNone(dict_jiben[u'股东及出资信息'])
        self.assertTrue(dict_jiben.has_key(u'变更信息'))
        self.assertIsNotNone(dict_jiben[u'变更信息'])
    # @unittest.skip("annual report")
    def test_table_equity_change(self):
        dict_jiben = self.analyser.parse_page(self.page, 'gudongguquan')
        self.assertTrue(dict_jiben.has_key(u'股权变更信息'))
        self.assertIsNotNone(dict_jiben[u'股权变更信息'])
    # @unittest.skip("annual report")
    def test_table_inproper(self):
        dict_jiben = self.analyser.parse_page(self.page, 'zhishichanquan')
        self.assertTrue(dict_jiben.has_key(u'知识产权出质登记信息'))
        self.assertIsNotNone(dict_jiben[u'知识产权出质登记信息'])

class OtherDepartPages(TestGuangdong0):
    def setUp(self):
        TestGuangdong0.setUp(self)
        self.url = urls['other_dept_pub_url']
        self.page = self.crawler.crawl_page_by_url(self.url)['page']

    def test_table_admin_permission(self):
        dict_jiben = self.analyser.parse_page(self.page, 'xingzhengxuke')
        self.assertTrue(dict_jiben.has_key(u'行政许可信息'))
        self.assertIsNotNone(dict_jiben[u'行政许可信息'])

    def test_table_admin_sanction(self):
        dict_jiben = self.analyser.parse_page(self.page, 'xingzhengchufa')
        self.assertTrue(dict_jiben.has_key(u'行政处罚信息'))
        self.assertIsNotNone(dict_jiben[u'行政处罚信息'])

def suite_ind_comm_pub_pages():
    suite = unittest.TestSuite()
    suite.addTest(IndCommPubPages('test_table_basic_page'))
    suite.addTest(IndCommPubPages('test_table_beian_page'))
    suite.addTest(IndCommPubPages('test_table_equity_ownership'))
    suite.addTest(IndCommPubPages('test_table_movable_property'))
    suite.addTest(IndCommPubPages('test_table_administration_sanction'))
    suite.addTest(IndCommPubPages('test_table_business_exception'))
    suite.addTest(IndCommPubPages('test_table_violate_law'))
    suite.addTest(IndCommPubPages('test_table_spot_check'))
    # suite.addTest(TestMain('test_run_crawl_ind_comm_pub_pages'))
    # suite.addTest(TestMain('test_run_crawl_ent_pub_pages'))
    # suite.addTest(TestMain('test_run_crawl_other_dept_pub_pages'))
    # suite.addTest(TestMain('test_run_crawl_judical_assist_pub_pages'))

    return suite

if __name__ == "__main__":
    # method 1
    # unittest.main()
    # method 2
    # runner = unittest.TextTestRunner()
    # suite1 = suite_ind_comm_pub_pages()
    # runner.run(suite1)
    # method 3 , this method can be used to test several classes
    suite0 = unittest.TestLoader().loadTestsFromTestCase(TestMain)
    suite1 = unittest.TestLoader().loadTestsFromTestCase(IndCommPubPages)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(EntPubPages)
    suite3 = unittest.TestLoader().loadTestsFromTestCase(OtherDepartPages)
    suites= unittest.TestSuite([suite1, suite2, suite3])
    runner = unittest.TextTestRunner()
    runner.run(suites)

