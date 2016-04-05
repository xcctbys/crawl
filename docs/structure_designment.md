# Statement of Goals 目标描述

* 结构化层主要实现解析采集器爬取的源数据，从中提取一些特定字段的数据存储到目标数据库。

# Functional Description 功能说明

## 解析器和导出器

- 输入: MongoDB
- 输出: MongoDB、MySQL
- 逻辑流程

        ## in master

        # main
        if is_duplicates():
            remove_duplicates()
        else:
            notify_dispatcher()

        # remove_duplicates
        ...

        # notify_dispatcher
        @handle_error
        conf = read_config()
        parser = generate_parser(conf)
        publish_to_slave(parser)

        # generate_parser
        @handle_error
        ...

        # publish_to_slave
        @handle_error
        server_id = load_balance(priority)
        publish(server_id, parser)

        ## in slave

        # parser
        source_data = read_mongo(job_id)
        target_mongo_data = parse_source(source_data)
        write_mongo(target_mongo_data)
        target_mysql_data = parse_target(target_mongo_data)
        write_mysql(target_mysql_data)
        write_log(succeed)

        # read_mongo
        @handle_error
        ...

        # parse_source
        @handle_error

        # write_mongo
        @handle_error

        # parse_target
        @handle_error

        # write_mysql
        @handle_error

        # write_log

- 性能
- 有哪些失败可能，失败后如何处理
    * slave节点解析器解析失败，失败后重启指定次数并记录错误日志，仍然解析失败生成报警日志
    * 其他失败记录错误日志

- 有哪些限制

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

