# coding=utf-8
from bs4 import BeautifulSoup
from itertools import izip


def wipe_off_newline_and_blank(data):
    """
    去除字符串中所有的换行,空格,制表符
    """
    data = str(data)
    data = data.replace('\n', '')
    data = data.replace('\t', '')
    data = data.replace(' ', '')
    return data.encode(encoding='utf-8')


def wipe_off_newline_and_blank_for_fe(data):
    """
    去除字符串首尾中的换行,空格,还有制表符
    """
    return wipe_off_newline_and_blank(data)


# table 分类:
# ================
#        A
# (tr)      标题
# (tr)子标题|子标题|子标题|
# (tr)内容 | 内容 | 内容 |
# (tr)内容 | 内容 | 内容 |
# ================
#                   B
#                  标题
# (tr)子标题A|子标题B|子标题C|子标题A|子标题B|子标题C|
# (tr)内容a | 内容b | 内容c |内容a | 内容b | 内容c |
# (tr)内容a | 内容b | 内容c |内容a | 内容b | 内容c |
# ================
#                   C
# (tr)            标题
# (tr)|子标题th | 内容td |子标题th| 内容 |
# (tr)|子标题th | 内容td |
# (tr)|子标题th | 内容td |子标题th| 内容 |


# 针对table A 可以使用如下方法
def parse_table_A(table):
    """
    # ================
    #        A
    # (tr)      标题th
    # (tr)子标题th|子标题th|子标题th|
    # (tr)内容td | 内容td | 内容td |
    # (tr)内容td | 内容td | 内容td |
    """
    if table is None:
        return None
    trs = table.find_all('tr')  # 获得表A中所有的 tr
    if len(trs) < 2:  # 当表中不同是存在标题子标题时 返回空
        return None
    # 获得 标题
    title_th = trs[0].find('th')
    if title_th is None and trs[0].get_text() is None:
        return None
    title = wipe_off_newline_and_blank(title_th)
    child_titles = []
    ths = trs[1].find_all('th')
    for th in ths:  # 取得所有子标题
        child_title = wipe_off_newline_and_blank(th.get_text())
        child_titles.append(child_title)

    count = 2  # 从2开始
    data = []
    while count < len(trs):
        content = {}
        tds = trs[count].find_all('td')
        if tds is None or len(tds) < len(child_titles):
            count += 1
            continue
        for td, child in izip(tds, child_titles):
            td_content = wipe_off_newline_and_blank(td.get_text())
            content[child] = td_content
        data.append(content)
        count += 1
    return data
