# coding: utf-8

import csv
import sqlite3
import StringIO


class No2Name(object):
    """docstring for No2Name"""

    def __init__(self, in_path, out_path):
        self.in_path = in_path
        self.out_path = out_path
        self.city_path = 'city_no.txt'
        self.cities = {}
        self.out_companes = []

    def load_companes(self):
        self._load_cities()
        company_noes = open(self.in_path, "r")
        company_noes_reader = csv.reader(company_noes, delimiter=' ', quotechar='|')
        for row in company_noes_reader:
            rows = str(row[0]).split(',')
            # print(rows)
            if rows[1] is None:
                continue
            city_no = str(rows[1])[0:2]
            city_name = self._transform_no2name(city_no)
            if city_name is not None:
                self.out_companes.append(
                        [city_no, str(rows[0]).strip(" "), str(city_name).strip(' '), str(rows[1]).strip(' ')])

    def _transform_no2name(self, city_no):
        if city_no in self.cities:
            return self.cities[city_no]
        else:
            return

    # def no2name(self):
    #     self.out_companes

    def _load_cities(self):
        file_cities = open(self.city_path, 'r')
        cities_reader = csv.reader(file_cities, delimiter=' ', quotechar='|')
        for row in cities_reader:
            [no, city] = row[0].split(",")
            self.cities[no] = str(city)

    def out_file(self):
        self._load_cities()
        self.load_companes()
        self.out_companes.sort()
        out_file = open(self.out_path, 'w')
        out_file.write('公司名,城市,注册号\r\n')
        for company in self.out_companes:
            city = self._transform_no2name(company[0])
            line = str(company[1] + ',' + city + ',' + company[3])
            line = line.strip(" ")
            line = line + '\r\n'
            out_file.write(line)
        out_file.close()

    def out_db(self,db_name):
        cx = sqlite3.connect('db_name')
        cx.text_factory = str
        cursor = cx.cursor()
        cursor.execute("create table if not exists company(id integer primary key,  city_id text not null,name text not null UNIQUE,city text not null, company_id text not null UNIQUE)")
        for company in self.out_companes:
            try:
                cursor.execute("insert into company(city_id, name, city, company_id) values(?, ?, ?, ?)", company)
            except Exception:
                print 'UNIQUE constraint failed'
        cx.commit()
        #生成内存数据库脚本
        str_buffer = StringIO.StringIO()
        #con.itrdump() dump all sqls 
        for line in cx.iterdump():
            str_buffer.write('%s\n' % line)
        cx.close()

        #打开文件数据库
        con_file = sqlite3.connect(db_name)
        cur_file = con_file.cursor()
        #执行内存数据库脚本
        cur_file.executescript(str_buffer.getvalue())
        #关闭文件数据库
        cur_file.close()


# if __name__ = '__main__':
no2Name = No2Name('company_no.csv', 'company_out.csv')
no2Name.out_file()
no2Name.out_db('company_out.db')
# no2Name.load_companes()
# no2Name.out_companes.sort()
# for company in no2Name.out_companes:
#     print(company)
