## 配置文件功能描述

用 JSON 定义目标数据库及其表信息, 程序根据配置文件, 读取 JSON 格式的源数据, 导出结构化数据到目标数据库

## 如何使用

- 每个网站使用1个配置文件. 
- 每个配置文件, 根据源数据的结构, 按模板格式修改需自定义的部分, 包括"数据库设置", "映射设置", "数据表设置"三个部分

## 配置文件格式

```
{
    "database": {
        "source_file": ["源数据文件1", "源数据文件2", "源数据文件3"], 
        "source_db": {
            "dbtype": "原始数据库类型",
            "host": "源数据库地址",
            "port": "源数据库端口",
            "username": "源数据库用户名",
            "password":, "源数据库秘密",
            "dbname": "源数据库名"
        },
        "destination_db": {
            "dbtype": "目标数据库类型",
            "host": "目标数据库地址",
            "port": "目标数据库端口",
            "username": "目标数据库用户",
            "password": "目标数据库秘码",
            "dbname": "目标数据库库名"
        }
    },

    "mapping": {
        "表1": {
            "name": "表1的英文名",
            "path": ["表1的表名在JSON源数据中的搜索路径"]
            "fields": {
                "字段1": "字段1英文名",
                "字段2": "字段2英文名",
                "字段n": "字段n英文名"
            },
        "表2": {
            "name": "表2英文名",
            "path": ["表2的表名在JSON源数据中的搜索路径"]
            "associated_field_path": {
                "关联字段": ["关联字段在JSON源数据中的搜索路径"]
            },
            "fields": {
                "关联字段": "关联字段英文名",
                "字段1": "字段1英文名",
                "字段2": "字段2英文名",
            },
        "表n": {
            "name": "表n英文名",
            "path": ["表n的表名在JSON源数据中的搜索路径"]
            "fields": {
                "字段1": "字段1英文名",
                "字段2": "字段2英文名",
            }
    },

    "table": {
        "表1英文名": [
			{
				"field": "字段1英文名",
				"datatype": "数据类型",
				"option": "字段选项"
			},
			{
				"field": "字段2英文名,
				"datatype": "数据类型",
				"option": "字段选项"
			},
			{
				"field": "字段n英文名,
				"datatype": "数据类型",
				"option": "字段选项"
			}
		],
		"表2英文名": [
            {
                "field": "关联字段英文名",
                "datatype": "数据类型",
                "option": "字段选项"
            },
			{
				"field": "字段1英文名,
				"datatype": "数据类型",
				"option": "字段选项"
			},
			{
				"field": "字段2英文名,
				"datatype": "数据类型",
				"option": "字段选项"
			}
		],
		"表n英文名": [
			{
				"field": "字段1英文名,
				"datatype": "数据类型",
				"option": "字段选项"
			},
			{
				"field": "字段2英文名,
				"datatype": "数据类型",
				"option": "字段选项"
			}
		]
	}
}
```
关于 mapping 部分: 
指定JSON源数据和关系数据库字段的映射关系和中英文表名的对应关系
- name 自定义表的英文名称
- path 一个列表, 用于指明如何在 JSON 源数据中找到表名, 根据源数据的嵌套层次, 依次写入列表
- associated_field_path 有的表数据在JSON的嵌套内层, 需关联一个外部的键, 此处指明外部键的路径. 如果关联子段是JSON最顶层的键可不指明路径
- fields 关系数据库表中字段的定义 

以工商为例, 某家企业信息的源始数据是这样的:
```
{
    "450100400000389": {
        "ind_comm_pub_reg_basic": {}, 
        "ent_pub_ent_annual_report": [
            {
                "序号": "1", 
                "报送年度": "2014年度报告", 
                "发布日期": "2015年6月19日", 
                "详情": {
                    "股权变更信息": [ ], 
                    "网站或网店信息": [ ], 
                    "股东及出资信息": [
                        {
                            "认缴出资方式": "货币", 
                            "认缴出资额（万元）": "18,552.59", 
                            "出资时间": "1994年3月18日", 
                            "认缴出资时间": "1994年3月18日", 
                            "实缴出资额（万元）": "18,552.59", 
                            "股东": "SUNMODE LIMITED", 
                            "出资方式": "货币"
                        }, 
                        {
                            "认缴出资方式": "货币", 
                            "认缴出资额（万元）": "700", 
                            "出资时间": "1994年3月18日", 
                            "认缴出资时间": "1994年3月18日", 
                            "实缴出资额（万元）": "700", 
                            "股东": "阳光壹佰置业集团有限公司", 
                            "出资方式": "货币"
                        } 
                    ], 
                    "对外提供保证担保信息": [ ], 
                    "企业基本信息": {}
                }
            }, 
            {}
        ] 
    }
}
```
现需获取"企业年报基本信息", 年报中的"股东及出资信息", mapping 中应这样写: 
```
{
    "mapping": {
        "ent_pub_ent_annual_report": {
            "name": "ent_pub_ent_annual_report",
            "path": ["ent_pub_ent_annual_report"],
            "fields": {
                "注册号/统一社会信用代码": "register_num",
                "序号": "order_num",
                "报送年度": "report_year",
                "发布日期": "putlish_date"
            }
        },
		"股东及出资信息": {
			"name": "shareholder_contrib",
			"path": ["ent_pub_ent_annual_report", "详情", "股东及出资信息"],
            "associated_field_path": {
                "报送年度": ["ent_pub_ent_annual_report"]
            },
			"fields": {
                "报送年度": "report_year",
				"注册号/统一社会信用代码": "register_num",
				"股东": "shareholder_name",
				"认缴出资方式": "subscribed_contrib_form",
				"认缴出资额": "subscribed_capital_contrib",
				"认缴出资时间": "subscribed_contrib_date",
				"出资方式": "contrib_form",
				"出资时间": "contrib_date",
				"实缴出资额": "actural_capital_contrib"
			}
		}
    },
	"table": {
		"ent_pub_ent_annual_report": [
			{
				"field": "order_num",
				"datatype": "INT",
				"option": "NOT NULL"
			},
			{
				"field": "register_num",
				"datatype": "INT",
				"option": "NOT NULL PRIMARY KEY"
			},
			{
				"field": "report_year",
				"datatype": "DATE",
				"option": ""
			},
			{
				"field": "publish_date",
				"datatype": "DATE",
				"option":""
			}
		],
		"shareholder_contrib": [
			{
				"field": "report_year",
				"datatype": "DATE",
				"option": ""
			},
			{
				"field": "register_num",
				"datatype": "INT",
				"option": "NOT NULL"
			},
			{
				"field": "shareholder_name",
				"datatype": "CHAR(100)",
				"option": ""
			},
			{
				"field": "subscribed_capital_contrib",
				"datatype": "VARCHAR(1000)",
				"option": ""
			},
			{
				"field": "subscribed_contrib_date",
				"datatype": "DATE",
				"option": ""
			},
			{
				"field": "subscribed_contrib_form",
				"datatype": "CHAR(50)",
				"option": ""
			},
			{
				"field": "actural_capital_contrib",
				"datatype": "VARCHAR(1000)",
				"option": ""
			},
			{
				"field": "contrib_date",
				"datatype": "DATE",
				"option": ""
			},
			{
				"field": "contrib_form",
				"datatype": "CHAR(50)",
				"option": ""
			}
		]
	}
}

```
其中"注册号/统一社会信用代码"为JSON最顶层的键"450100400000389", 不用在associated_field_path中写出;
"报送年度"在内部, 需在 associated_field_path 中写明路径


## 注意事项

- 用户仅可以更改模板中中文标明的数据
- 可以添加任意张表, 每张表可以添加任意个字段, 保持模板中的格式, 并且和mapping中项目一致即可(列表最后一项后不要加逗号)
- 目标数据库现只支持 MySQL

