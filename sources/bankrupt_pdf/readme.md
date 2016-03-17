##破产文书 pdf_crawler 阅读文档

###代码及文件说明：

* settings.py:为配置文件


    * pdf_restore_dir = './pdf' #所有PDF的根目录，生成的PDF会以/year/month/day/all_pdf 的形式存储在该目录下,并且会有一个 data_pdf.json文件（字典，key(url):value(abspath_pdf)
    * json_list_dir = './json' #程序首先得从url地址下载昨天的.json.gz文件，并以20160120.json的文件格式放置在该目录下
    * host = 'http://clawer.princetechs.com:8080/media/clawer_result' #下载json.gz文件所对应url的前部分
    * ID = '29' ##下载json.gz文件所对应url的ID部分,加上一个日期就可以完全的构造出事个 url

* settings_pro.py：

    * log_level = logging.WARN
    * log_file = '/data/pdf_crawler/result_pdf/crawler.log'
    *logger = None
    * pdf_restore_dir = '/data/pdf_crawler/pdf'
    * json_restore_dir = '/data/pdf_crawler/json'
    * host = 'http://clawer.princetechs.com:8080/media/clawer_result'
    * ID = '29'
    * 与settings.py大致相同，只是目录指定为绝对路径。

* run.py简单说明：

    - 采用多进程形式。一个json文件中的一行数据 为一个进程。
    * 1,首先根据url下载昨天的json.gz并解压缩。
    * 2,判断运行参数，使用都没有给定 日期 参数，则根据已经下载 yesterday.json 解析出每一个 pdf所对应的 url，并利用requests.get()下载好pdf文件，并以url地址的最后 digits.pdf 为文件名保存在配置文件 /data/pdf_crawler/result_pdf/year/month/day/all_digits.pdf.如果给定参数，如 python run.py 100 20160120,则会下载对就日期2016年1月20日的pdf,处理方式相同。
    * 注意：在运行的过程中，requests.get()方法不一定能够一次性下载好完整的pdf文件，一定得判断resp.content是否为空，如果为空，则得重新下载。我设定最多下载10次。
    * 3,由于 python日志模块 及 python邮件 还不是很熟悉，目前还没有这两项功能，但已经有过尝试，还在努力补充。

### 生产环境部署

* 使用settings_pro.py 配置文件，设置环境变量  PDF_CRAWLER_SETTINGS='settings_pro'
* 整个文件夹pdf_crawler放置于/data/目录下（在settings_pro.py文件里有设置）

### 运行程序：

* python run.py max_crawl_time [ 20160120 …]
* 没有设置日期则会自动下载昨天的PDF
* 例如：python run.py 100 or python run.py 100 20160120


### 结果
* pdf目录下为对应日期下的所有pdf文件
* json目录下为对应日期下的json文件，及添加字段的 'data_insert'.json文件。如：
```javascript
{
            "abs_path": "./pdf/2016/01/25/4398856.pdf",
            "pdf_url": "http://rmfygg.court.gov.cn/psca/lgnot/bulletin/download/4398856.pdf",
            "publishdate": "2016-01-22",
            "content": "本院根据天津荣智科技发展有限公司申请，于2015年12月23日作出（2015）南民破字第0066号民事裁定书，裁定受理债务人破产清算的申请，并依法指定天津荣智科技发展有限公司破产清算组为管理人。管理人的地址天津市河东区津塘路18号鼎泰大厦1506室，邮编300171，联系电话（022）24450408。债权人应于2016年3月15日前向管理人申报债权，并提交有关证明材料。逾期未申报债权的，依据《中华人民共和国企业破产法》第五十六条的规定处理。天津荣智科技发展有限公司的债务人或者财产持有人应向破产管理人清偿债务或者交付财产。第一次债权人会议于2016年4月27日（星期三）上午10时在天津市南开区人民法院召开，地址天津市南开区保山道108号。债权人出席会议应向本院提交营业执照、个人或法定代表人身份证明、授权委托书。",
            "courtcode": "天津市南开区人民法院",
            "party": "天津荣智科技发展有限公司"
}
```
其中'abs_path'为新增加的key.
