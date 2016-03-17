#encoding=utf-8
import os

from enterprise.models import Province

from .libs.beijing_crawler import BeijingCrawler
from .libs.chongqing_crawler import ChongqingClawer
from .libs.tianjin_crawler import TianjinCrawler
##
from .libs.zhejiang_crawler import ZhejiangCrawler
from .libs.shandong_crawler import ShandongCrawler
from .libs.xinjiang_crawler import XinjiangClawer
from .libs.yunnan_crawler import YunnanCrawler
from .libs.neimenggu_crawler import NeimengguClawer
##
from .libs.henan_crawler import HenanCrawler
from .libs.hainan_crawler import HainanCrawler
from .libs.jilin_crawler import JilinCrawler
from .libs.xizang_crawler import XizangCrawler
from .libs.shaanxi_crawler import ShaanxiCrawler
##
from .libs.shanghai_crawler import ShanghaiCrawler
from .libs.zongju_crawler import ZongjuCrawler
from .libs.jiangsu_crawler import JiangsuCrawler
from .libs.heilongjiang_crawler import HeilongjiangClawer
from .libs.shanxi_crawler import ShanxiCrawler
##
from .libs.gansu_crawler import GansuClawer
from .libs.guangdong_crawler import GuangdongClawer
from .libs.guangxi_crawler import GuangxiCrawler
from .libs.anhui_crawler import AnhuiCrawler
from .libs.fujian_crawler import FujianCrawler
##
from .libs.guizhou_crawler import GuizhouCrawler
from .libs.hebei_crawler import HebeiCrawler
from .libs.hubei_crawler import HubeiCrawler
from .libs.hunan_crawler import HunanCrawler
from .libs.liaoning_crawler import LiaoningCrawler
##
# from .libs.ningxia_crawler import NingxiaClawer
from .libs.qinghai_crawler import QinghaiCrawler
from .libs.sichuan_crawler import SichuanCrawler
from .libs.jiangxi_crawler import JiangxiCrawler


from .libs import settings
import urlparse


class EnterpriseDownload(object):
    PROVINCES = [
        {"id": Province.BEIJING, "class": BeijingCrawler},
        {"id": Province.CHONGQING, "class": ChongqingClawer},
        {"id": Province.TIANJIN, "class": TianjinCrawler},
        {'id': Province.ZHEJIANG, 'class': ZhejiangCrawler},
        {'id': Province.SHANDONG, 'class': ShandongCrawler},
        {'id': Province.XINJIANG, 'class': XinjiangClawer},
        {'id': Province.YUNNAN, 'class': YunnanCrawler},
        {'id': Province.NEIMENGGU, 'class': NeimengguClawer},
        #####
        {'id': Province.HENAN, 'class': HenanCrawler},
        {'id': Province.HAINAN, 'class': HainanCrawler},
        {'id': Province.JILIN, 'class': JilinCrawler},
        {'id': Province.XIZANG, 'class': XizangCrawler},
        {'id': Province.SHAANXI, 'class': ShaanxiCrawler},
        ####
        {'id': Province.SHANGHAI, 'class': ShanghaiCrawler},
        {'id': Province.ZONGJU, 'class': ZongjuCrawler},
        {'id': Province.JIANGSU, 'class': JiangsuCrawler},
        {'id': Province.HEILONGJIANG, 'class': HeilongjiangClawer},
        {'id': Province.SHANXI, 'class': ShanxiCrawler},
        ###
        {'id': Province.GANSU, 'class': GansuClawer},
        {'id': Province.GUANGDONG, 'class': GuangdongClawer},
        {'id': Province.GUANGXI, 'class': GuangxiCrawler},
        {'id': Province.ANHUI, 'class': AnhuiCrawler},
        {'id': Province.FUJIAN, 'class': FujianCrawler},
        ###
        {'id': Province.GUIZHOU, 'class': GuizhouCrawler},
        {'id': Province.HEBEI, 'class': HebeiCrawler},
        {'id': Province.HUBEI, 'class': HubeiCrawler},
        {'id': Province.HUNAN, 'class': HunanCrawler},
        {'id': Province.LIAONING, 'class': LiaoningCrawler},
        ###
        # {'id': Province.NINGXIA, 'class': NingxiaClawer},
        {'id': Province.QINGHAI, 'class': QinghaiCrawler},
        {'id': Province.SICHUAN, 'class': SichuanCrawler},
        {'id': Province.JIANGXI, 'class': JiangxiCrawler},

    ]

    def __init__(self, url):
        """ url format:
        enterprise://${province}/${enterprise_name}/${register_no}/?${querystring}
        """
        self.url = url
        if os.path.exists(settings.json_restore_path) is False:
            os.makedirs(settings.json_restore_path, 0775)

        o = urlparse.urlparse(self.url)
        self.province = o.hostname

        tmp = filter(lambda x: x.strip() != "", o.path.split("/"))
        if len(tmp) != 2:
            raise Exception("'%s' format invalid" % self.url)

        self.name = tmp[0]
        self.register_no = tmp[1]

    def download(self):
        """ Returns: json data
        """
        province_id = Province.to_id(self.province)
        for item in self.PROVINCES:
            if item['id'] != province_id:
                continue

            cls = item['class'](settings.json_restore_path)
            data = cls.run(self.register_no)
            return data

        raise Exception(u"unknown province %s" % self.province)

