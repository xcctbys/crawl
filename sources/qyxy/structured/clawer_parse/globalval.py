# -*- coding: utf-8 -*-
import os


class GlobalVal():
 
    def __init__(self):
        self.count_parsed = 0
        self.count_all = 0
        self.count_update = 0

    @staticmethod
    def set_count_zero():
        GlobalVal.count_parsed = 0
        GlobalVal.count_all = 0
        GlobalVal.count_update = 0

    @staticmethod
    def count_parsed_plusone():
        GlobalVal.count_parsed += 1

    @staticmethod
    def count_all_plusone():
        GlobalVal.count_all += 1

    @staticmethod
    def count_update_plusone():
        GlobalVal.count_update += 1

    @staticmethod
    def get_count_parsed():
        return GlobalVal.count_parsed

    @staticmethod
    def get_count_all():
        return GlobalVal.count_all

    @staticmethod
    def get_count_update():
        return GlobalVal.count_update

  