#encoding=utf-8

from django.db import models
from django.conf import settings
import urlparse

# Create your models here.

class Category(models.Model):
    (NORMAL, 
     YUNSUAN, 
     ZHIHU, 
     JIANGSHU,
     TIANJIN,
     JIANGXI,
     CHONGQING,
     SICHUAN,
     GUIZHOU,
     XIZHUANG,
     QINHAI,
     NINGXIA,
     XINJIANG,
     QUANGUO,
     GUANGDONG,
     SHANGHAI,
     HEBEI,
     SHANXI,
     NEIMENGGU,
     LIAONING,
     JILIN,
     HEILONGJIANG,
     ZHEJIANG,
     ANHUI,
     FUJIAN,
     SHANDONG,
     GUANGXI,
     HAINAN,
     HENAN,
     ALL,
     ALL_1,
     ) = range(1, 32)
    
    full_choices = (
        (NORMAL, u"北京字母", 'http://qyxy.baic.gov.cn/CheckCodeCaptcha?currentTimeMillis=1444875766745&num=87786', 300),
        (YUNSUAN, u"运算类型", "http://qyxy.baic.gov.cn/CheckCodeYunSuan?currentTimeMillis=1447655192940&num=48429", 300),
        (ZHIHU, u"知乎字母", "http://www.zhihu.com/captcha.gif?r=1448087287415", 300),
        (JIANGSHU, u"江苏", "http://www.jsgsj.gov.cn:58888/province/rand_img.jsp?type=7", 300),
        (TIANJIN, u"天津", "http://tjcredit.gov.cn/verifycode", 300),
        (JIANGXI, u"江西", "http://gsxt.jxaic.gov.cn/ECPS/verificationCode.jsp", 300),
        (CHONGQING, u"重庆", "http://gsxt.cqgs.gov.cn/sc.action?width=130&height=40&fs=23&t=1449473139130", 300),
        (SICHUAN, u"四川", 'http://gsxt.scaic.gov.cn/ztxy.do?method=createYzm&dt=1449473634428&random=1449473634428', 300),
        (GUIZHOU, u"贵州", 'http://gsxt.gzgs.gov.cn/search!generateCode.shtml?validTag=searchImageCode&1449473693892', 300),
        (XIZHUANG, u"西藏", 'http://gsxt.xzaic.gov.cn/validateCode.jspx?type=0&id=0.6980565481876813', 300),
        (QINHAI, u"青海", 'http://218.95.241.36/validateCode.jspx?type=0&id=0.9130336582967944', 300),
        (NINGXIA, u"宁夏", 'http://gsxt.ngsh.gov.cn/ECPS/verificationCode.jsp?_=1449473855952', 300),
        (XINJIANG, u"新疆", 'http://gsxt.xjaic.gov.cn:7001/ztxy.do?method=createYzm&dt=1449473880582&random=1449473880582', 300),
        (QUANGUO, u"全国-汉字", 'http://gsxt.saic.gov.cn/zjgs/captcha?preset=&ra=0.6737781641715337', 1000),
        (GUANGDONG, u"广东", 'http://gsxt.gdgs.gov.cn/aiccips/verify.html?random=0.6461621058211715', 1000),
        (SHANGHAI, u"上海", 'https://www.sgs.gov.cn/notice/captcha?preset=1&ra=0.13763015669048162', 1000),
        (HEBEI, u"河北", "http://www.hebscztxyxx.gov.cn/notice/captcha?preset=1&ra=0.12507317386321537", 300),
        (SHANXI, u"山西", 'http://218.26.1.108/validateCode.jspx?type=1&id=0.5561280730741579', 1000),
        (NEIMENGGU, u"内蒙古", 'http://www.nmgs.gov.cn:7001/aiccips/verify.html?random=0.15379660368246195', 1000),
        (LIAONING, u"辽宁", 'http://gsxt.lngs.gov.cn/saicpub/commonsSC/loginDC/securityCode.action?tdate=47736', 300),
        (JILIN, u"吉林", 'http://211.141.74.198:8081/aiccips/securitycode?0.9858144849658483', 1000),
        (HEILONGJIANG, u"黑龙江", 'http://gsxt.hljaic.gov.cn/validateCode.jspx?type=1&id=0.37630681760147366', 1000),
        (ZHEJIANG, u"浙江", '', 0),
        (ANHUI, u"安徽", 'http://www.ahcredit.gov.cn/validateCode.jspx?type=1&id=0.41052326137836004', 1000),
        (FUJIAN, u"福建", 'http://wsgs.fjaic.gov.cn/creditpub/captcha?preset=str-00&ra=0.7105599333444296', 300),
        (SHANDONG, u"山东", 'http://218.57.139.24/securitycode?0.07734315576514572', 1000),
        (GUANGXI, u"广西", 'http://gxqyxygs.gov.cn/validateCode.jspx?type=1&id=0.49213323240661666', 1000),
        (HAINAN, u"海南", "", 0),
        (HENAN, u"河南", "http://222.143.24.157/validateCode.jspx?type=1&id=0.9717317246571591", 1000),
        (ALL, u"全国工商总局-字母", 'http://gsxt.saic.gov.cn/zjgs/captcha?preset=1&ra=0.6737781641715337', 600),
        (ALL_1, u"全国工商总局-字母1", 'http://gsxt.saic.gov.cn/zjgs/captcha?preset=1&ra=0.6737781641715337', 300),
    )
    
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=1024)
    max_number = models.IntegerField(default=0)
    
    class Meta:
        app_label = "captcha"
    

class Captcha(models.Model):
    url = models.URLField()
    category = models.IntegerField()
    image_hash = models.CharField(max_length=32)
    label_count = models.IntegerField(default=0)
    add_datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "captcha"
    
    def image_url(self):
        return urlparse.urljoin(settings.MEDIA_URL, "captcha/%d/%s" % (self.category, self.image_hash))
    
    def label_logs(self):
        return LabelLog.objects.filter(captcha=self)
    
    def as_json(self):
        result = {"id": self.id,
            "category": self.category,
            "image_hash": self.image_hash,
            "labels": [x.label for x in self.label_logs()],
            "image_url": self.image_url(),
        }
        return result
        
        
class LabelLog(models.Model):
    captcha = models.ForeignKey(Captcha)
    label = models.CharField(max_length=32)
    ip = models.IPAddressField()
    add_datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "captcha"
        

