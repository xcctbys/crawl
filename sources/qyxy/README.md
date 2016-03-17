# Program Rules

- 每个省份对应一个爬虫文件，utf-8文件编码格式，命名方式为：`${Province}_crawler.py`。代码格式如下：

        class ${Province}Clawer(object):     #请替换${Province}为省名，如BeiJing
        
            def __init__(self, json_restore_path):
                """ Args:
                json_restore_path: 存放破解的验证码或是其他临时文件
                """
                pass

            def run(self, register_no):
                """ Get all data of enterprise by register_no, and return it.
                Args:
                    register_no: 企业注册号
                Returns:
                    string, which is json format.
                """
                
                return ""

    - 网络请求使用 requests 包
    - 日志使用 logging 包
    - 解析网页使用 beautifulsoup
    - 中间不要依赖非标准库的包
    - 也不要引入settings文件的任何配置内容
    
    - 最后，这个文件还需要复制到`../../clawer/enterprise/libs/`，该目录运行的是分布式版本
    
            
- settings.py 是所有爬虫的配置文件
- model 里面存放的是破解识别码需要的建模数据，每个省对应一个文件夹
- enterprise_list 里面放的是所有的企业名单，现在暂时是一个省一个文件，比如： beijing.txt
- CaptchaRecognition.py 是破解图片识别码的类，使用方法如下：

        from CaptchaRecognition import CaptchaRecognition
    
        recognition = CaptchaRecognition("beijing")  #support jiangshu etc
        result = recognition.predict_result(im_path)  # result is image code


## settings.py 说明


	#log
	log_level = logging.WARN
	log_file = '/data/clawer_result/enterprise/crawler.log'
	logger = None

	save_html = True   # 是否保存html

	html_restore_path = './enterprise_crawler'  #如果save_html为True，html存储在子目录下。子目录以省份命名。

	json_restore_path = './enterprise_crawler'   #最后结果转为json，输出到子目录下。子目录格式：${省份名}/${YEAR}/${MONTH}/ 。 每天一个文件，需要使用zlib压缩，文件名格式为； ${DAY}.json.gz 。 每行对应一个企业的JSON对象。

	enterprise_list_path = './enterprise_list/'  # 企业名单，每个省对应一个文件，如北京为beijing.txt

## 输出格式
    #每行一个企业，为一个key-value对，key为企业的注册号，value为一个字典，里面包含所有页面解析后的信息。
    {ent_number_1: {all_data_of_ent_1}}
    {ent_number_2: {all_data_of_ent_2}}
    ....
    #all_data为该企业所有页面解析后的数据，具体包括：
    (一) 工商公示信息
    (1) 'ind_comm_pub_reg_basic': 登记信息-基本信息
    (2) 'ind_comm_pub_reg_shareholder': 登记信息-股东信息
    (3) 'ind_comm_pub_reg_modify': 登记信息-变更信息
    (4) 'ind_comm_pub_arch_key_persons': 备案信息-主要人员信息
    (5) 'ind_comm_pub_arch_branch': 备案信息-分支机构信息
    (6) 'ind_comm_pub_arch_liquidation': 备案信息-清算信息
    (7) 'ind_comm_pub_movable_property_reg': 动产抵押登记信息
    (8) 'ind_comm_pub_equity_ownership_reg': 股权出置登记信息
    (9) 'ind_comm_pub_administration_sanction': 行政处罚信息
    (10) 'ind_comm_pub_business_exception': 经营异常信息
    (11) 'ind_comm_pub_serious_violate_law': 严重违法信息
    (12) 'ind_comm_pub_spot_check': 抽查检查信息

    (二) 企业公示信息
    (1) 'ent_pub_ent_annual_report': 企业年报
    (2) 'ent_pub_shareholder_capital_contribution': 企业投资人出资比例
    (3) 'ent_pub_equity_change': 股权变更信息
    (4) 'ent_pub_administration_license': 行政许可信息
    (5) 'ent_pub_knowledge_property': 知识产权出资登记
    (6) 'ent_pub_administration_sanction': 行政许可信息
    (7) 'ent_pub_reg_modify': 变更信息
    
    (三) 其他部门公示信息
    (1) 'other_dept_pub_administration_license': 行政许可信息
    (2) 'other_dept_pub_administration_sanction': 行政处罚信息

    (四) 司法协助公示信息
    (1) 'judical_assist_pub_equity_freeze': 股权冻结信息
    (2) 'judical_assist_pub_shareholder_modify': 股东变更信息

    在all_data 中的各个最顶层的key-value对的key为 以上的各个名称，比如工商公示信息-登记信息-基本信息的key为 'ind_comm_pub_reg_basic'  
    value为 从页面中爬取的工商公示信息-登记信息-基本信息的具体数据。

    具体数据有两种类型：普通键值对构成的字典、列表。普通的字典格式对应于页面上不规则的表格数据(比如 工商公示信息-登记信息-基本信息的表格);  
    列表格式对应于页面上规则的记录类型的表格，比如 工商公示信息-登记信息-股东信息。有些表格中含有详情页连接，详情页的数据爬取后作为value放在对应的位置。
    
    具体的json格式，参见 json_data_example 目录下的文件。

## 代码说明

crawler.py 中定义了 CrawlerUtils 类，封装了一些常用的函数；

- Crawler 类，为爬虫类的基类，其他爬虫最好从该类继承；
- Parser 类，为解析页面的基类，其他的页面解析类最好继承于它，因为其中封装了一些可能会用到的解析html表格的函数。


# 生产环境部署

使用`settings_pro.py` 配置文件，设置环境变量 `ENT_CRAWLER_SETTINGS='settings_pro'`

## 运行程序

    python run.py max_crawl_time province_list
