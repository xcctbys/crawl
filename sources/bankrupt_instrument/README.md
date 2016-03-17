### Configuration

当前文件夹中包括：
| InstrumentParsing.py
| InstrumentSplit.py
| LawPaperBase.py
| bankrupt_instrument.sh
| initial.sh
| sys
  | Configuration.cfg

其中 InstrumentParsing.py 为解析的主文件，可以添加一个arguement，以定义配置文件地址。

Configuration.cfg 为默认的配置文件，如果自定义新的配置文件，请仿照这个格式配置。

仅需要运行bankrupt_instrument.sh。

initial.sh可用于创建数据库

程序仅需要每天零时运行一次。

# 注意：另外当前文件夹需要和json文件放置在同一个服务器中。