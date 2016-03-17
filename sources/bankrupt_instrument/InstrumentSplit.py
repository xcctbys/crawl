# encoding=utf-8

import jieba
from math import sqrt
import jieba.posseg as pseg
import copy


class InstrumentSplit(object):
    @staticmethod
    def cut_to_dataset(cuts, dataset):
        _list = [0] * len(dataset)
        for word in cuts:
            index = dataset.index(word)
            _list[index] += 1
        return _list

    def cut_to_list(self, cuts):
        _list = []
        for word in cuts:
            _list.append(word)
        return _list

    def cosine_sim(self, x_a, x_b):
        a_length = len(x_a)
        b_length = len(x_b)
        if a_length >= b_length:
            return self.consine(x_a, x_b)
        else:
            return self.consine(x_b, x_a)

    def consine(self, x_a, x_b):
        a_length = len(x_a)
        b_length = len(x_b)
        product_sum = 0.
        sum_a = 0.
        sum_b = 0.
        for i in range(a_length):
            a = x_a[i]
            if i >= b_length:
                b = 0
            else:
                b = x_b[i]
            product_sum += a * b
            sum_a += a ** 2
            sum_b += b ** 2
        consine = product_sum / (sqrt(sum_a) * sqrt(sum_b))
        return consine

    def get_enterprise_names(self, words):
        seg_list = pseg.cut(words)
        START = False
        name_list = []
        names = set()
        previous_word = None
        stop_words = [u"管理人"]
        special_words = [u"律师事务所"]
        for word, flag in seg_list:
            if flag == "ns" and not START:
                START = True
                name_list = []
                name_list.append(word)
            elif word.__contains__(u"公司") and START:
                name_list.append(word)
                START = False
                name = u"".join(name_list)
                names.add(name)
            elif previous_word is not None and word in stop_words and START:
                START = False
                name = u"".join(name_list)
                names.add(name)
            elif START:
                if len(name_list) > 10 or word in special_words:
                    START = False
                else:
                    name_list.append(word)
            previous_word = word
        return list(names)

    @staticmethod
    def occur(itrbl, x, nth):
        return (i for pos, i in enumerate(indx for indx, elem in enumerate(itrbl)
                                          if elem == x)
                if pos == nth - 1).next() if x in itrbl \
            else   None

    def split(self, content):
        words = copy.copy(content)
        names = self.get_enterprise_names(words)

        for name in names:
            words = words.replace(name, "")

        terms = list(set(self.cut_to_list(jieba.cut(words))))

        word_split = words.split(u"。")
        sim_content = []
        i = 0
        while i < len(word_split) - 2:
            sentence1 = word_split[i]
            flags1 = self.cut_to_dataset(jieba.cut(sentence1), terms)
            if sentence1 == "":
                continue
            for k in range(i + 1, len(word_split)):
                sentence2 = word_split[k]
                if sentence2 == "":
                    continue
                flags2 = self.cut_to_dataset(jieba.cut(sentence2), terms)
                similarity = self.cosine_sim(flags1, flags2)
                if similarity > 0.8:
                    sim_content.append(k)
                    i += k
                    break
            i += 1
            if len(sim_content) != 0 and i >= sim_content[0]:
                break


        content_split = []
        if len(sim_content) == 0:
            content_split.append(content)
        else:
            previous_index = 0
            for s_i in sim_content:
                end_index = self.occur(content, u"。", s_i) + 1
                content_split.append(content[previous_index:end_index])
                previous_index = end_index
        return content_split
