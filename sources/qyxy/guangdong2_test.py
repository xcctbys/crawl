#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import unittest
from Guangdong2 import Guangdong2


urls ={
        "main": "http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo_3au/If33vWye5UuPp+iY6u6FQtJGDUruMalngHz1ONi2UJ96uTS+QaKhmOwDSFMD-7kW54gFL28iQmsO8Qn3cTA==",
        "ind_comm_url" : "http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo_3au/If33vWye5UuPp+iY6u6FQtJGDUruMalngHz1ONi2UJ96uTS+QaKhmOwDSFMD-7kW54gFL28iQmsO8Qn3cTA==",
        "ent_pub_url" : "http://gsxt.gdgs.gov.cn/aiccips/BusinessAnnals/BusinessAnnalsList.html",
        "other_dept_pub_url": "http://gsxt.gdgs.gov.cn/aiccips/OtherPublicity/environmentalProtection.html",
        "judical_assist_url": "http://gsxt.gdgs.gov.cn/aiccips/judiciaryAssist/judiciaryAssistInit.html",
        'prefix_GSpublicity':'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=',
        }

class TestGuangdong2(unittest.TestCase):
    def setUp(self):
        self.guangdong = Guangdong2()

        self.crawler = self.guangdong.crawler
        self.analyser = self.guangdong.analysis
        page_entInfo = self.crawler.crawl_page_by_url(urls['main'])['page']
        self.post_data = self.analyser.parse_page_data_2(page_entInfo)
    def tearDown(self):
        self.guangdong = None
        self.post_data= None

class TestMain(TestGuangdong2):

    def test_run_crawl_ind_comm_pub_pages(self):
        data = self.crawler.crawl_ind_comm_pub_pages(urls['ind_comm_url'],2, self.post_data)
        print data
        self.assertIsNotNone(data)

    def test_run_crawl_ent_pub_pages(self):
        data = self.crawler.crawl_ent_pub_pages(urls['ent_pub_url'],2, self.post_data)
        print data
        self.assertIsNotNone(data)

    def test_run_crawl_other_dept_pub_pages(self):
        data = self.crawler.crawl_other_dept_pub_pages(urls['other_dept_pub_url'],2, self.post_data)
        print data
        self.assertIsNotNone(data)

    def test_run_crawl_judical_assist_pub_pages(self):
        data = self.crawler.crawl_judical_assist_pub_pages(urls['judical_assist_url'],2, self.post_data)
        print data
        self.assertIsNotNone(data)

class IndCommPubPages(TestGuangdong2):

    def test_table_basic_page(self):
        url = urls['prefix_GSpublicity']+'entInfo'
        page = self.crawler.crawl_page_by_url_post(url, self.post_data)['page']
        dict_jiben = self.analyser.parse_page_2(page, 'jibenxinxi', self.post_data)
        self.assertTrue(dict_jiben.has_key(u'股东信息'))
        self.assertIsNotNone(dict_jiben[u'股东信息'])
        self.assertTrue(dict_jiben.has_key(u'基本信息'))
        self.assertIsNotNone(dict_jiben[u'基本信息'])
        self.assertTrue(dict_jiben.has_key(u'变更信息'))
        self.assertIsNotNone(dict_jiben[u'变更信息'])

    def test_table_beian_page(self):
        url = urls['prefix_GSpublicity']+'entCheckInfo'
        page = self.crawler.crawl_page_by_url_post(url, self.post_data)['page']
        dict_jiben = self.analyser.parse_page_2(page, 'beian', self.post_data)
        self.assertTrue(dict_jiben.has_key(u'主要人员信息'))
        self.assertIsNotNone(dict_jiben[u'主要人员信息'])
        self.assertTrue(dict_jiben.has_key(u'分支机构信息'))
        self.assertIsNotNone(dict_jiben[u'分支机构信息'])

        self.assertTrue(dict_jiben.has_key(u'清算信息'))
        self.assertIsNotNone(dict_jiben[u'清算信息'])

    def test_table_equity_ownership(self):
        url = urls['prefix_GSpublicity']+'curStoPleInfo'
        page = self.crawler.crawl_page_by_url_post(url, self.post_data)['page']
        dict_jiben = self.analyser.parse_page_2(page, 'guquanchuzhi', self.post_data)
        self.assertTrue(dict_jiben.has_key(u'股权出质登记信息'))
        self.assertIsNotNone(dict_jiben[u'股权出质登记信息'])

    def test_table_movable_property(self):
        url = urls['prefix_GSpublicity']+'pleInfo'
        page = self.crawler.crawl_page_by_url_post(url, self.post_data)['page']
        dict_jiben = self.analyser.parse_page_2(page, 'dongchandiya', self.post_data)
        self.assertTrue(dict_jiben.has_key(u'动产抵押信息'))
        self.assertIsNotNone(dict_jiben[u'动产抵押信息'])

    def test_table_administration_sanction(self):
        url = urls['prefix_GSpublicity']+'cipPenaltyInfo'
        page = self.crawler.crawl_page_by_url_post(url, self.post_data)['page']
        dict_jiben = self.analyser.parse_page_2(page, 'xingzhengchufa', self.post_data)
        self.assertTrue(dict_jiben.has_key(u'行政处罚信息'))
        self.assertIsNotNone(dict_jiben[u'行政处罚信息'])

    def test_table_business_exception(self):
        url = urls['prefix_GSpublicity']+'cipUnuDirInfo'
        page = self.crawler.crawl_page_by_url_post(url, self.post_data)['page']
        dict_jiben = self.analyser.parse_page_2(page, 'jingyingyichang', self.post_data)
        self.assertTrue(dict_jiben.has_key(u'经营异常信息'))
        self.assertIsNotNone(dict_jiben[u'经营异常信息'])

    def test_table_violate_law(self):
        url = urls['prefix_GSpublicity']+'cipBlackInfo'
        page = self.crawler.crawl_page_by_url_post(url, self.post_data)['page']
        dict_jiben = self.analyser.parse_page_2(page, 'yanzhongweifa', self.post_data)
        self.assertTrue(dict_jiben.has_key(u'严重违法信息'))
        self.assertIsNotNone(dict_jiben[u'严重违法信息'])

    def test_table_spot_check(self):
        url = urls['prefix_GSpublicity']+'cipSpotCheInfo'
        page = self.crawler.crawl_page_by_url_post(url, self.post_data)['page']
        dict_jiben = self.analyser.parse_page_2(page, 'chouchajiancha', self.post_data)
        self.assertTrue(dict_jiben.has_key(u'抽查检查信息'))
        self.assertIsNotNone(dict_jiben[u'抽查检查信息'])

class EntPubPages(TestGuangdong2):
    def test_table_annual_report(self):
        url = "http://gsxt.gdgs.gov.cn/aiccips/BusinessAnnals/BusinessAnnalsList.html"
        page = self.crawler.crawl_page_by_url_post(url, self.post_data)['page']
        dict_jiben = self.analyser.parse_page_2(page, 'qiyenianbao', self.post_data)
        self.assertTrue(dict_jiben.has_key(u'qiyenianbao'))
        self.assertIsNotNone(dict_jiben[u'qiyenianbao'])

    def test_table_permission(self):
        url ="http://gsxt.gdgs.gov.cn/aiccips/AppPerInformation.html"
        page = self.crawler.crawl_page_by_url_post(url, self.post_data)['page']
        dict_jiben = self.analyser.parse_page_2(page, 'appPer', self.post_data)
        self.assertTrue(dict_jiben.has_key(u'行政许可情况'))
        self.assertIsNotNone(dict_jiben[u'行政许可情况'])

    def test_table_sanction(self):
        url ="http://gsxt.gdgs.gov.cn/aiccips/XZPunishmentMsg.html"
        page = self.crawler.crawl_page_by_url_post(url, self.post_data)['page']
        dict_jiben = self.analyser.parse_page_2(page, 'xzpun', self.post_data)
        self.assertTrue(dict_jiben.has_key(u'行政处罚情况'))
        self.assertIsNotNone(dict_jiben[u'行政处罚情况'])

    def test_table_shareholder_capital(self):
        url ="http://gsxt.gdgs.gov.cn/aiccips/ContributionCapitalMsg.html"
        page = self.crawler.crawl_page_by_url_post(url, self.post_data)['page']
        dict_jiben = self.analyser.parse_page_2(page, 'sifapanding', self.post_data)
        self.assertTrue(dict_jiben.has_key(u'股东及出资信息'))
        self.assertIsNotNone(dict_jiben[u'股东及出资信息'])
        self.assertTrue(dict_jiben.has_key(u'变更信息'))
        self.assertIsNotNone(dict_jiben[u'变更信息'])

    def test_table_equity_change(self):
        url = "http://gsxt.gdgs.gov.cn/aiccips/GDGQTransferMsg/shareholderTransferMsg.html"
        page = self.crawler.crawl_page_by_url_post(url, self.post_data)['page']
        dict_jiben = self.analyser.parse_page_2(page, 'guquanbiangeng', self.post_data)
        self.assertTrue(dict_jiben.has_key(u'股权变更信息'))
        self.assertIsNotNone(dict_jiben[u'股权变更信息'])

    def test_table_inproper(self):
        url = "http://gsxt.gdgs.gov.cn/aiccips/intPropertyMsg.html"
        page = self.crawler.crawl_page_by_url_post(url, self.post_data)['page']
        dict_jiben = self.analyser.parse_page_2(page, 'inproper', self.post_data)
        self.assertTrue(dict_jiben.has_key(u'知识产权出质登记信息'))
        self.assertIsNotNone(dict_jiben[u'知识产权出质登记信息'])

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
    suite1 = unittest.TestLoader().loadTestsFromTestCase(IndCommPubPages)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(EntPubPages)
    suites= unittest.TestSuite([suite1])
    runner = unittest.TextTestRunner()
    runner.run(suites)

