# Statement of Goals 目标描述

    结构化层主要实现解析采集器爬取的源数据，从中提取一些特定字段的数据存储到目标数据库。

# Functional Description 功能说明

## 去重器

- 功能

        判断要结构化的源数据是否已经存在，若存在根据配置文件检测是否要更新，需要更新返回False否则返回True；若不存在返回True。True表示源数据已经结构化，False表示源数据未结构化。

- 输入: 源数据
- 输出: True | False
- ORM

        # 存储已经解析过的源文件
        class Structrued():
            fields...

- 逻辑流程

        is_duplicates(data):
            exist = Structured.objects.filter(source=data)
            if not exist:
                if check_update():
                    return True
                else:
                    return False
            else:
                return True

## 调度器（In master）

        负责分配解析任务，首先读取配置（TODO: 根据文件格式或URI）选择对应的解析器（HTML，JSON，PDF，OCR），然后根据任务优先级和slave节点们的负载选择任务最终分配的机器，返回sid（Server Id），最后将任务发布到sid对应的服务器。

- 输入: 任务Id
- 输出: None
- 逻辑流程

        @handle_error
        notify_dispatcher(job_id):
            conf = read_config(job_id)
            parser = generate_parser(conf)
            server_id = load_balance(priority)
            publish(server_id, parser)


## 解析器

        解析源数据为JSON格式的目标数据，其中JSON的键是运营人员配置的，最终将JSON文件存入MongoDB。若解析过程中出现错误记录错误日志，并根据重启策略重启，如果策略失效生成报警日志结束解析。

- 输入: job_id
- 输出: None
- 逻辑流程

        @handle_error
        parse_to_json(job_id):
            keys = read_mongo(job_id)
            source = read_mongo(job_id)
            target = parse_source(source, keys)
            write_mongo(target)
            write_log(succeed)


## 导出器

        1. 生成Mysql数据表
        2. 从解析的JSON数据中提取特定字段的数据，并做中英文映射，其中映射关系需要运营人员配置，最终存入指定数据库中。

- 输入: job_id
- 输出: None
- 逻辑流程

        @handle_error
        create_mysql_schema(job_id):
            conf = read_mongo(job_id)
            tables = parse(conf)
            for table in tables:
                insert(table)

        @handle_error
        extract_fields_to_mysql(job_id):
            source = read_mongo(job_id)
            target = extract_fields(source)
            write_mysql(target)
            write_log(succeed)

# User Interface 用户界面

## 登陆界面

## 编程接口

- 调用方式
- 输入
- 输出
- 例子


# Internel 内部实现

## Directory 代码目录结构

    λ ~/Projects/cr-clawer/clawer/structure/ dev* tree
    .
    ├── __init__.py
    ├── admin.py
    ├── migrations
    │   └── __init__.py
    ├── models.py
    ├── tests
    │   └── __init__.py
    └── views.py

    2 directories, 6 files

## Database 数据库


# Test 测试

## Testcase 1

- 依赖
- 输入
- 期望输出


# Other

- 参考文档: <https://www.toptal.com/freelance/why-design-documents-matter>

