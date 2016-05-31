# encoding=utf-8

# import os
import json
# import datetime
# from urllib import unquote
import re


class BaiduTextAnalysis(object):
    pattern_date = u"[\s0-9一二三四五六七八九十零〇○]{2,5}[\.\/-－年]{1}[\s0-9一二三四五六七八九十零〇○]{1,2}[\.\/-－月]{1}[\s0-9一二三四五六七八九十零〇○]{1,2}[\.\/-－日]{0,1}"
    pattern_date_1 = u"[\s0-9一二三四五六七八九十零〇○]{2,5}\.[\s0-9一二三四五六七八九十零〇○]{1,2}\.[\s0-9一二三四五六七八九十零〇○]{1,2}"

    def text_analysis(self, html, url, keywords):
        try:
            enterprise = keywords.split("_")[0]
            keyword = keywords.split("_")[1]

            html = self.remove_script(html)
            html = self.remove_style(html)
            html = html.decode("utf-8")
            page_title = get_page_title(html)
            body = self.get_body(html)
            body = re.sub("<[^>]*>", "", body)
            body = body.replace("\\r", "").replace("\\t", "").replace(
                "\t", "").replace("  ", "").replace("\n\n", "").replace("\n\n", "")
            date = self.get_date(body)
            category = self.get_category(body)
            if category == u"其他":
                _dict_ = {}
            else:
                _dict_ = {
                    "url":url,
                    "enterprise":enterprise,
                    "date":date,
                    "category":category
                }
            return json.dumps(_dict_)
        except:
            return json.dumps({})

    def get_ps(self, html):
        start_pattern = '<p'
        end_pattern = '</p>'
        get_script_start = html.split(start_pattern)
        get_script_end = html.split(end_pattern)
        start_index = []
        end_index = []

        length_end = len(end_pattern)
        record = ""
        for s in get_script_start:
            record += s
            start_index.append(len(record))
            record += start_pattern

        record = ""
        for e in get_script_end:
            record += e + end_pattern
            end_index.append(len(record))
        previous_s = None
        previous_e = None
        bias = False
        pairs = []
        for si in range(len(start_index)):
            s = start_index[si]
            e = end_index[si]
            if previous_s is None:
                previous_s = s
                previous_e = e
            if e < s:
                if not bias:
                    pairs.append((previous_e + len("</p>"), e))
                    bias = True
                else:
                    pairs.append((previous_s, e))
            else:
                pairs.append((s, e))
            previous_s = s
            previous_e = e
        return pairs

    def check_title_style(self, title):
        if title == "OpenLaw":
            return None
        style = u"[\u4e00-\uffffa-zA-Z0-9]{2,}"
        garbled = re.findall(style, title)
        if len(garbled) != 0:

            return True
        else:
            return None

    def get_page_title(self, content):
        content_removed = re.sub("\+?\+", " ", content)
        title = re.findall("<title>([\\n\\s\\S\w\W\u0000-\uffff]{1,200})</title>", content_removed)
        if len(title) == 0:
            return ""
        title = title[0].replace("\n", "").replace(" ", "")
        return title

    def remove_script(self, content):
        start_pattern = '<script'
        end_pattern = '</script>'
        get_script_start = content.split(start_pattern)
        get_script_end = content.split(end_pattern)
        start_index = []
        end_index = []
        if len(get_script_start) == 0:
            return body
        if len(get_script_end) == 0:
            return body

        record = ""
        for s in get_script_start:
            record += s
            start_index.append(len(record))
            record += start_pattern

        record = ""
        for e in get_script_end:
            record += e + end_pattern
            end_index.append(len(record))

        patterns = []
        index_l = 0
        index_r = 0
        pre_right = 0
        while (index_l < min(len(end_index), len(start_index)) and
                       index_r < min(len(end_index), len(start_index))):
            left = start_index[index_l]
            if left < pre_right:
                index_l += 1
                continue
            right = end_index[index_r]
            index_l += 1
            index_r += 1
            pre_right = right
            patterns.append(content[left:right])
        for pattern in patterns:
            content = content.replace(pattern, "")
        return content

    def remove_style(self, content):
        start_pattern = '<style'
        end_pattern = '</style>'
        get_script_start = content.split(start_pattern)
        get_script_end = content.split(end_pattern)
        start_index = []
        end_index = []
        if len(get_script_start) == 0:
            return body
        if len(get_script_end) == 0:
            return body

        length_end = len(end_pattern)
        record = ""
        for s in get_script_start:
            record += s
            start_index.append(len(record))
            record += start_pattern

        record = ""
        for e in get_script_end:
            record += e + end_pattern
            end_index.append(len(record))

        index_pattern = []
        patterns = []
        index_l = 0
        index_r = 0
        pre_right = 0
        while (index_l < min(len(end_index), len(start_index)) and
                       index_r < min(len(end_index), len(start_index))):
            left = start_index[index_l]
            if left < pre_right:
                index_l += 1
                continue
            right = end_index[index_r]
            index_l += 1
            index_r += 1
            pre_right = right
            patterns.append(content[left:right])
        for pattern in patterns:
            content = content.replace(pattern, "")
        return content

    def get_body(self, content):
        body = re.findall("<body[^>]*>([\\n\s\S\w\W\u0000-\uffff]*)</body>", content)
        if len(body) == 0:
            return None
        else:
            return body[0]

    def get_category(self, content):
        category = u""
        if category.__contains__(u"子公司"):
            category += u"子公司"
        for cat in [u"借款", u"不正当竞争", u"股东权", u"买卖合同"]:
            if content.__contains__(cat):
                category += cat
                break
        if category == u"":
            return u"其他"
        else:
            return category + u"纠纷"

    def check_date_style(self, date):
        date_part = date.split("/")
        if len(date_part) != 3:
            return None
        if len(date_part[0]) != 4:
            return None
        else:
            try:
                year = int(date_part[0])
                if year not in range(1949, 2020):
                    return None
            except:
                return None
        if len(date_part[1]) not in [1, 2]:
            return None
        else:
            try:
                month = int(date_part[1])
                if month not in range(1, 13):
                    return None
            except:
                return None
        if len(date_part[2]) not in [1, 2]:
            return None
        else:
            try:
                day = int(date_part[2])
                if day not in range(1, 32):
                    return None
            except:
                return None
        return True

    def get_date(self, content):

        content = content.replace(" ", "").replace("\t", "").replace("\n\n", "").replace("\n\n", "")
        dates = re.findall(self.pattern_date, content)
        dates += re.findall(self.pattern_date_1, content)

        date_set = set()
        for d in dates:
            if (d.__contains__(u"年") and d.__contains__(u"月")) or len(d.split("/")) == 3 or len(
                    d.split("-")) == 3 or len(d.split(".")) == 3:
                d_checker = self.convert_date(d).split("/")[0]
                try:
                    d_checker = int(d_checker)
                    if d_checker >= 2000 and d_checker <= 2016:
                        date_set.add(d)
                except:
                    continue

        if len(date_set) == 1:
            return self.convert_date(list(date_set)[0])

        category = self.get_category(content)
        if category == u"其他":
            return "其他"

        category = category.replace(u"子公司", u"").replace(u"纠纷", u"")

        closed_time = None
        distance = None

        removed_content = re.sub(u"[^0-9a-zA-Z\u4e00-\u9fa5\.\/\-－○〇]+", "", content)
        cate_index = np.array([m.start() for m in re.finditer(category, removed_content)])
        for date in date_set:
            date_index = [m.start() for m in re.finditer(date, removed_content)]
            for i in date_index:
                if self.check_special_phase(removed_content[i - 10:i + 10]):
                    return self.convert_date(date)
                if removed_content[i - 5:i + 5].__contains__(u"出生") or removed_content[i - 5:i + 5].__contains__(u"生日"):
                    continue
                min_distance = abs(min(cate_index - i))
                if distance is None or distance > min_distance:
                    distance = min_distance
                    closed_time = date

        if closed_time is None:
            return "没日期"
        return self.convert_date(closed_time)

    def check_special_phase(self, sentence):
        words = [u"日期", u"时间", u"判员", u"审判", u"书记"]

        for word in words:
            checker = 0
            for c in word:
                if sentence.__contains__(c):
                    checker += 1
                else:
                    continue
            if checker == len(word):
                return True
        return False

    def convert_number(self, chinese):
        dates_dict_0 = {
            u"二十一": "21", u"二十二": "22", u"二十三": "23", u"二十四": "24", u"二十五": "25",
            u"二十六": "26", u"二十七": "27", u"二十八": "28", u"二十九": "29", u"三十": "30", u"三十一": "31",
            u"元": "1"
        }
        dates_dict_1 = {u"十一": "11", u"十二": "12", u"十三": "13", u"十四": "14", u"十五": "15",
                        u"十六": "16", u"十七": "17", u"十八": "18", u"十九": "19", u"二十": "20",}
        dates_dict_2 = {u"〇": "0", u"零": "0", u"一": "1", u"二": "2", u"三": "3", u"○": "0",
                        u"四": "4", u"五": "5", u"六": "6", u"七": "7",
                        u"八": "8", u"九": "9", u"十": "10", u" ": "", "\t": "", "\n": ""}
        for c, n in dates_dict_0.iteritems():
            chinese = chinese.replace(c, n)
        for c, n in dates_dict_1.iteritems():
            chinese = chinese.replace(c, n)
        for c, n in dates_dict_2.iteritems():
            chinese = chinese.replace(c, n)
        return chinese

    def convert_date(self, date):
        new_date = date.replace(u"日", "")
        new_date = new_date.replace(" ", "")
        new_date = self.convert_number(new_date)
        if new_date.find(u"年") == 2:
            new_date = "20" + new_date if int(new_date[:2]) < 20 else "19" + new_date
        elif new_date.find(u"年") == 3:
            new_date = "2" + new_date if int(new_date[:1]) == 0 else "1" + new_date
        for replaced in [u"年", u"月", u"日", u"-", u"－", u"／", u"."]:
            new_date = new_date.replace(replaced, "/")
        return new_date

