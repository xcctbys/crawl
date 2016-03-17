# encoding=utf-8


from datetime import datetime
import re
import os
import jieba
import jieba.analyse
import jieba.posseg as pseg
import pandas as pd

jieba.add_word(u"管理人", tag="n")
jieba.add_word(u"债权人", tag="n")
jieba.add_word(u"债务人", tag="n")
jieba.add_word(u"申请人", tag="n")
jieba.add_word(u"被申请人", tag="n")
jieba.add_word(u"中华人民共和国企业破产法", tag="n")
jieba.add_word(u"信用合作联社", tag="n")
jieba.add_word(u"有限责任公司", tag="n")
jieba.add_word(u"有限公司", tag="n")
jieba.add_word(u"东方", tag="sn")
jieba.add_word(u"东营市", tag="ns")
jieba.add_word(u"双牌县", tag="ns")
jieba.add_word(u"玉环县", tag="ns")
jieba.add_word(u"玉环", tag="ns")
jieba.add_word(u"正汉", tag="nt")
jieba.add_word(u"子午", tag="nt")
jieba.add_word(u"百年", tag="nt")
jieba.add_word(u"开发区", tag="ns")
jieba.add_word(u"技术开发区", tag="ns")
jieba.add_word(u"迎宾路", tag="ns")
jieba.add_word(u"律师事务所", tag="n")
jieba.add_word(u"第一", tag="nm")
jieba.add_word(u"第二", tag="nm")
jieba.add_word(u"第三", tag="nm")
jieba.add_word(u"第四", tag="nm")
jieba.add_word(u"第五", tag="nm")
jieba.add_word(u"第六", tag="nm")
jieba.add_word(u"第七", tag="nm")
jieba.add_word(u"第一次", tag="m")
jieba.add_word(u"第二次", tag="m")
jieba.add_word(u"第三次", tag="m")
jieba.add_word(u"第四次", tag="m")
jieba.add_word(u"第五次", tag="m")
jieba.add_word(u"会议室", tag="s")
jieba.add_word(u"八楼", tag="n")
jieba.add_word(u"万士", tag="n")
jieba.add_word(u"万", tag="nm")
jieba.add_word(u"十", tag="nm")
jieba.add_word(u"百", tag="nm")
jieba.add_word(u"千", tag="nm")
jieba.add_word(u"亿", tag="nm")
jieba.add_word(u"兆", tag="nm")
jieba.add_word(u"佰", tag="nm")
jieba.add_word(u"办公室", tag="ns")
jieba.add_word(u"第二会议室", tag="ms")
jieba.add_word(u"多斯巴亿", tag="n")
jieba.add_word(u"哈密道", tag="ns")
jieba.add_word(u"周口市", tag="ns")
jieba.add_word(u"佰恩", tag="n")
jieba.add_word(u"连云港", tag="ns")
jieba.add_word(u"日内", freq=100000, tag="nm")
jieba.add_word(u"楚雄", tag="ns")
jieba.add_word(u"张家港", tag="ns")
jieba.add_word(u"对外", tag="n")
jieba.add_word(u"海安", tag="ns")
jieba.add_word(u"电白县", tag="ns")
jieba.add_word(u"大同市", tag="ns")
jieba.add_word(u"南通", tag="ns")
jieba.add_word(u"被", freq=100000000, tag="np")
jieba.add_word(u"破产人", freq=100000, tag="n")
jieba.add_word(u"遵义", tag="ns")
jieba.add_word(u"牡丹", tag="n")
jieba.add_word(u"炭黑", tag="n")
jieba.add_word(u"海利", tag="n")
jieba.add_word(u"振兴", tag="nv")
jieba.add_word(u"开发", tag="nv")
jieba.add_word(u"回收", tag="nv")
jieba.add_word(u"之日起", tag="j")
jieba.add_word(u"制造", tag="nv")


class LawPaperBase(object):
    @staticmethod
    def convert_number(chinese):
        dates_dict_0 = {
            u"二十一": "21", u"二十二": "22", u"二十三": "23", u"二十四": "24", u"二十五": "25",
            u"二十六": "26", u"二十七": "27", u"二十八": "28", u"二十九": "29", u"三十": "30", u"三十一": "31",
            u"元": "1"
        }
        dates_dict_1 = {u"十一": "11", u"十二": "12", u"十三": "13", u"十四": "14", u"十五": "15",
                        u"十六": "16", u"十七": "17", u"十八": "18", u"十九": "19", u"二十": "20",}
        dates_dict_2 = {u"〇": "0", u"零": "0", u"一": "1", u"二": "2", u"三": "3",
                        u"四": "4", u"五": "5", u"六": "6", u"七": "7",
                        u"八": "8", u"九": "9", u"十": "10", u" ": "", "\t": "", "\n": "", u"○": "0"}
        for c, n in dates_dict_0.iteritems():
            chinese = chinese.replace(c, n)
        for c, n in dates_dict_1.iteritems():
            chinese = chinese.replace(c, n)
        for c, n in dates_dict_2.iteritems():
            chinese = chinese.replace(c, n)
        return chinese

    def convert_date(self, date, publish_date=False):
        if not publish_date:
            date_pattern = u"[\s0-9一二三四五六七八九十零○〇]+年[\s0-9一二三四五六七八九十○零〇]+月[\s0-9一二三四五六七八九○十零〇]+[日]*"
            new_date = re.findall(date_pattern, date)[0]
            new_date += u"日" if not new_date.__contains__(u"日") else ""
            new_date = new_date.replace(" ", "")
            new_date = self.convert_number(new_date)
            if new_date.find(u"年") == 2:
                new_date = "20" + new_date
            try:
                dt = datetime.strptime(new_date.encode("utf-8"), u"%Y年%m月%d日".encode("utf-8"))
            except:
                dt = datetime.now()

        else:
            dt = datetime.strptime(date, "%Y-%m-%d")
        new_date = dt.strftime("%Y/%m/%d")
        return new_date

    @staticmethod
    def get_decision_date(dates, content, index):
        min_distance = None
        min_date = None
        if re.findall(u"自即日起生效", content):
            return None
        for d in dates:
            cur_index = content.find(d)
            #             print d
            if cur_index < index:
                if (index - cur_index) < min_distance or min_distance is None:
                    min_distance = index - cur_index
                    min_date = d
            else:
                length = len(content)
                if (length - cur_index) in range(8, 15) and min_distance > 15:
                    return d
        return min_date

    @staticmethod
    def mkdir(dirname):
        if not os.path.exists(dirname):
            os.mkdir(dirname)

    @staticmethod
    def get_timestamp():
        return datetime.strftime(datetime.datetime.now(), "%Y%m%d_%H%M%S")

    @staticmethod
    def get_today():
        return datetime.strftime(datetime.datetime.now(), "%Y%m%d")

    @staticmethod
    def check(name, previous, current, is_print=False):
        previous_stop = [u"律师事务所", u"人民政府", u"债权", u"债务", u"日内", u"内", u"听证会", u"下落不明"]
        previous_word, previous_flag = previous
        word, flag = current
        pattern = u"[0-9]"
        not_chinese = re.findall(pattern, name)
        if len(name) <= 4:
            if is_print:
                print "*" * 30, u"长度不符"
            return False
        if name[-1] == u"）" or name[-1] == u")":
            name = name[:-1]
        if len(name) <= 4:
            if is_print:
                print "*" * 30, u"长度不符"
            return False
        if len(name) >= 28 and not name.__contains__(u"、"):
            if is_print:
                print "*" * 30, u"长度过长", len(name)
            return False
        if len(not_chinese) != 0:
            if is_print:
                print "*" * 30, u"有非中文"
            return False
        if previous_flag in ["f"]:
            if is_print:
                print "*" * 30, u"前词词性"
            return False
        if name.__contains__(u"法院"):
            if is_print:
                print "*" * 30, u"含有法院"
            return False
        if previous_word in previous_stop:
            if is_print:
                print "*" * 30, u"前词在停止词中"
            return False
        if previous_word[-1] in [u"路", u"道"]:
            if is_print:
                print "*" * 30, u"存在路名"
            return False
        if word in [u"担任"]:
            if is_print:
                print "*" * 30, u"存在停止词"
            return False
        if flag in ["m"]:
            if is_print:
                print "*" * 30, u"结束词为数词"
            return False
        if name[-2] in [u"一", u"二", u"三", u"四", u"五", u"六", u"七", u"八", u"九", u"十"] and name[-1] != u"厂":
            if is_print:
                print "*" * 30, u"倒数第二个字为数词，最后一字不为规定词"
            return False
        if name.__contains__(u"即日起生效"):
            if is_print:
                print "*" * 30, u"含即日起生效"
            return False
        if name.__contains__(u"会计师事务所"):
            return False
        if name.__contains__(u"银行"):
            return False
        if name.__contains__(u"办公室"):
            return False
        if name[-2:] in [u"全体", u"财产", u"企业", u"综合"]:
            if is_print:
                print "*" * 30, u"结尾词为特殊词汇"
            return False
        return True

    def get_enterprise_name(self, content, is_print=False, print_name=False, check_print=False):
        seg_list = pseg.cut(content)
        START = False
        name_list = []
        names = []
        previous_word = None
        previous_flag = None
        is_replaced = False
        stop_words = [u"符合", u"以其", u"及其", u"等", u"合并", u"自", u"因", u"的债权人",
                      u"全体债权人", u"享有", u"法定代表", u"清算组", u"不能",
                      u"债权人", u"企业破产", u"指定", u"破产案", u"担任", u"法院",
                      u"提出", u"申请", u"进行", u"重整", u"清算", u"（以下", u"管理人",
                      u"中华人民共和国企业破产法", u"清偿债务", u"中华人民共和国民事诉讼法", u"中华人民共和国",
                      u"中华人民共和国破产法", u"股东", u"，", u":", u"：", u"。", u"董事会", u"强制", u"纳入", u"【", u"】", u" ", u"\n"]
        start_words = [u"债务人", u"终结", u"破产人", u"本院认为", u"被申请人", u"受理", u"根据", u"申请",
                       u"裁定", u"受理了", u"宣告", u"如下", u"受理的", u"立案", u"裁定将", u"批准"]
        reco_words = [u"对", u"确已", u"或", u"名下的", u"或者", u"债务人", u"被申请人",
                      u"：", u"申请人", u"下落不明", u"终结", u"破产", u"不足以"]
        great_stop_words = stop_words + start_words + reco_words
        keep_name = None
        replace_name = None
        just_added = False
        for word, flag in seg_list:
            if is_print:
                print word, flag, len(name_list), START, just_added
            if just_added and previous_word in [u"：", u":"]:
                break
            else:
                just_added = False
            if (flag == "ns" and not START and (word not in stop_words) and (previous_flag not in ["ns"])
                and previous_word not in [u"债权人"]):
                START = True
                name_list = []
                name_list.append(word)
                if is_print:
                    print "-" * 30, "first start"
            elif ((previous_word in start_words or
                       (previous_word is not None and
                                sum([1 if previous_word.__contains__(x) else 0 for x in [u"公司", u"旅馆"]]) > 0)
                   or (previous_word is not None and (previous_word + word) in start_words))
                  and word not in great_stop_words
                  and previous_word not in [u"的"]
                  and not START):
                if previous_word + word not in great_stop_words and flag not in ["x", "p"] and word not in start_words:
                    name_list = []
                    name_list.append(word)
                    START = True
                    if is_print:
                        print "-" * 30, "second start"
            elif (word in great_stop_words or (not flag.__contains__("n") and
                                                       flag not in ["a", "ag", "j", "b", "d", "i", "t",
                                                                    "v", "c", "f", "g", "zg", "x",
                                                                    "l", "s", "k", "p", "m", "q", "vg"])
                  or (previous_word is not None and previous_word + word in great_stop_words)):
                if START:
                    if previous_word + word in great_stop_words:
                        name_list = name_list[:-1]
                    name = "".join(name_list)
                    if replace_name is not None and name in replace_name and keep_name is not None:
                        name = keep_name
                    if self.check(name, (previous_word, previous_flag), (word, flag), check_print):
                        if (name.__contains__(u"（") or name.__contains__(u"(")):
                            if name.__contains__(u")") or name.__contains__(u"）"):
                                names.append(name)
                            else:
                                continue
                        elif name.__contains__(u")") or name.__contains__(u"）"):
                            if (name.__contains__(u"（") or name.__contains__(u"(")):
                                names.append(name)
                            else:
                                continue
                        else:
                            names.append(name)
                        just_added = True
                        if is_print:
                            print "-" * 30, "first end"
                        if print_name or is_print:
                            print "first case:", name

                START = False
            elif START:
                if previous_word is not None and (previous_word + word in [u"(以下", u"（以下", u"(简称", u"（简称", u"（下称"]):
                    name_list = name_list[:-1]
                    name = "".join(name_list)
                    if self.check(name, (previous_word, previous_flag), (word, flag), check_print):
                        if (name.__contains__(u"（") or name.__contains__(u"(")):
                            if name.__contains__(u")") or name.__contains__(u"）"):
                                names.append(name)
                            else:
                                continue
                        elif name.__contains__(u")") or name.__contains__(u"）"):
                            if (name.__contains__(u"（") or name.__contains__(u"(")):
                                names.append(name)
                            else:
                                continue
                        else:
                            names.append(name)
                        just_added = True
                        if is_print:
                            print "-" * 30, "second end"
                        if print_name or is_print:
                            print "second case:", name
                    START = False

                elif word not in start_words + reco_words:
                    name_list.append(word)

            if not is_replaced and previous_word is not None and (
                            previous_word + word in [u"(以下", u"（以下", u"(简称", u"（简称", u"（下称"]):
                addv_pattern = u"简称([\u0000-\uffff]{0,10})）"
                addv_pattern_1 = u"简称([\u0000-\uffff]{0,10})\)"
                addv_pattern_2 = u"下称([\u0000-\uffff]{0,10})\）"
                try:
                    addvs = re.findall(addv_pattern, content) + re.findall(addv_pattern_1, content)
                    addvs += re.findall(addv_pattern_2, content)
                    if len(addvs) > 0:
                        addv = addvs[0]
                        addv = list(set([addv] + re.findall(u"([\u4e00-\u9fa5]+)", addv)))
                        replace_name = addv
                        if len(names) == 0:
                            print "error: no keep name, and the current replace_name is", replace_name[0]
                        # print content
                        else:
                            keep_name = names[-1]
                            if is_print:
                                print "repalce_name = ", addv[0], "keep_name = ", keep_name
                                is_replaced = True
                except:
                    print "error:", content

            previous_word = word
            previous_flag = flag
            if word in [u"律师事务所"] and START:
                START = False

        if replace_name is not None:
            for replace in replace_name:
                for i in range(len(re.findall(replace, content))):
                    names.append(keep_name)

        if len(names) == 0:
            name_pattern = u"[各]{0,1}([\u4e00-\u9fa5]{5,20})[的]{0,1}债权人"
            name = re.findall(name_pattern, content)
            if len(name) > 0:
                return name[0], replace_name
            else:
                return "", replace_name

        df = pd.DataFrame(names, columns=["name"])
        df["count"] = 1
        df = df["count"].groupby(df["name"]).sum().to_frame()
        df["name"] = df.index
        df.index = range(len(df))
        try:
            if len(set(df["count"])) == 1:
                df["length"] = df["name"].map(lambda x: len(x))
                sort = df.sort_values(by="length", ascending=False)["name"]
                sort.index = range(len(sort))
                return_name = sort.iloc[0]
            else:
                sort = df.sort_values(by="count", ascending=False)["name"]
                sort.index = range(len(sort))
                return_name = sort.iloc[0]
        except:
            return_name = ""

        name_list = []
        for name in return_name.split(u"、"):
            and_char = re.findall(u"与", name)
            if len(and_char) < 2:
                for na in name.split(u"与"):
                    if len(na) > 4 and len(na) < 28:
                        name_list.append(na)

        return u"、".join(name_list), replace_name
