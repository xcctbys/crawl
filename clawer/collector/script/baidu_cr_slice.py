# encoding=utf-8

import logging
import re
import json
import urllib
import unittest
import traceback
import os
import cPickle as pickle
try:
    import pwd
except:
    pass
from bs4 import BeautifulSoup
import requests
import MySQLdb


from __future__ import absolute_import
import math
import hashlib
from struct import unpack, pack, calcsize
import redis
import urlparse
import sys
import StringIO
import cStringIO
from io import BytesIO
import datetime


requests.packages.urllib3.disable_warnings()
running_python_3 = sys.version_info[0] == 3
try:
    REDIS = "redis://10.0.1.3:6379/0"
    redis_addr=urlparse.urlparse(REDIS)
    redis_addr='redis://'+redis_addr[1]
except:
    redis_addr = None


<SLICE>
HOST = '10.0.1.3'
USER = 'cacti'
PASSWD = 'cacti'
PORT = 3306
STEP =  1 # 每个step取10个。
ROWS = 10
DEBUG = False  # 是否开启DEBUG
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")
# 所需爬取的相应关键词
KEYWORD = [
        u'违约',
        u'逾期',
        u'诉讼',
        u'纠纷',
        u'代偿',
        u'破产',
        u'清算'
]
class History(object):  # 实现程序的可持续性，每次运行时读取上次运行时保存的参数，跳到相应位置继续执行程序

    def __init__(self):
        # self.company_num = 0  # 初始化pickle中用作公司名称位置索引值
        self.total_page = 0
        self.current_page = 0
        self.path = "/tmp/baidu_company_search_<SLICE>"  # pickle文件存放路径（提交至平台的代码记住带上tmp前斜杠）

    def load(self):  # pickle的载入
        if os.path.exists(self.path) is False:  # 读取pickle失败则返回
            return

        with open(self.path, "r") as f:  # 打开pickle文件并载入
            old = pickle.load(f)
            # self.company_num = old.company_num  # 取出文件中存入的索引值
            self.total_page = old.total_page
            self.current_page = old.current_page

    def save(self):  # pickle的保存
        with open(self.path, "w") as f:
            pickle.dump(self, f)


class Generator(object):
    HOST = "https://www.baidu.com/s?"

    def __init__(self):  # 初始化
        self.uris = set()
        self.args = set()
        self.history = History()
        self.history.load()
        # self.source_url = "http://clawer.princetechs.com/enterprise/api/get/all/"
        self.enterprises= []
        self.step = STEP

    def search_url_with_batch(self):
        self.obtain_enterprises()
        de_ents =bloom_filter_api("uri_generator", self.enterprises)
        if len(de_ents) != len(self.enterprises):
            self.enterprises=[]
            self.enterprises.extend(de_ents)
            self.obtain_enterprises()
        for company in self.enterprises:
            # logging.debug("%s"%(company))
            for each_keyword in KEYWORD:  # 遍历搜索关键词
                keyword = each_keyword
                self.page_url(company, keyword)  # 传参调用url构造函数

    def obtain_enterprises(self, rows= ROWS):
        if self.history.current_page <= 0 and self.history.total_page <= 0:
            self._load_total_page()

        for _ in range(self.step):
            r = self.paginate(self.history.current_page, rows)
            self.history.current_page += 1
            self.history.total_page = r['total_page']

            for item in r['rows']:
                self.enterprises.append(item['name'])

            if self.history.current_page > self.history.total_page:
                self.history.current_page = 0
                self.history.total_page = 0
                # self.history.save()
                logging.debug("All finished of slice %d"%(SLICE))
                break
        logging.debug("slice done %d!"%(self.history.current_page+1))
        self.history.save()

    def _load_total_page(self):
        r = self.paginate(0, ROWS)
        self.history.current_page = 0
        self.history.total_page = r['total_page']
        self.history.save()

    def page_url(self, current_company, current_keyword):
        for page_num in range(0, 10, 10):  # 遍历实现baidu搜索结果页翻页（第一页为0，第二页为10，第三页为20...）
            params = {"wd": current_company.encode("gbk") + " " + current_keyword.encode("gbk"),
                      "pn": page_num}  # 构造url参数
            url = "%s%s" % (self.HOST, urllib.urlencode(params))  # 构造url
            r = requests.get(url, verify=False, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"})  # 浏览器代理请求url
            soup = BeautifulSoup(r.text, "html5lib")  # 使用html5lib解析页面内容
            contents = soup.find("div", {"id": "content_left"})  # 找到页面中id为content_left的div
            divs = contents.find_all("div", {"class": "result"})  # 在目标div中找到所有class为result的div
            for div in divs:  # 遍历divs获取每一条div
                all_em = div.h3.find_all("em")  # 找到div.h3标签中所有的em标签
                if len(all_em) > 1:
                    ems = [em.get_text().strip() for em in all_em] # 将em建为一个列表
                    if current_company in ems and current_keyword in ems: # 判断关键词是否在em标签中，若判断为真则使用浏览器代理获取目标url中的headers信息
                        target_head = requests.head(div.h3.a["href"], headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"}).headers
                        target_url = target_head["Location"]  # 获取目标链接真实url]
                        proto, rest = urllib.splittype(target_url)
                        host, rest = urllib.splithost(rest)
                        if "wenku.baidu.com" in host:  # 百度文库
                            continue
                        if "www.docin.com" in host:  # 豆丁
                            continue
                        if "www.doc88.com" in host:  # 道客巴巴
                            continue
                        if "vdisk.weibo.com" in host:  # 微博微盘
                            continue
                        if "www.pkulaw.cn/" in host:  # 北大法宝
                            continue
                        test = "%s%s%s%s%s" % (target_url, " ", current_company, "_", current_keyword)  # 将url、公司、关键字重新组合
                        self.uris.add(test)  # 将url加入uris中

    def paginate(self, current_page, rows=10):
        conn = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db='clawer', port=PORT,charset='utf8')
        sql = "select count(*) from enterprise_enterprise where slice = %d"%( SLICE)
        cur = conn.cursor()
        count = cur.execute(sql)
        total_rows =cur.fetchone()[0]
        total_page = total_rows/rows
        # print total_page
        if current_page  > total_page:
            current_page = 0
        sql = "select name from enterprise_enterprise where slice = %d limit %d, %d"%(SLICE ,current_page*rows, rows)
        count = cur.execute(sql)
        columns = [desc[0] for desc in cur.description]
        result = []
        for r in cur.fetchall():
            # for v in r:
                # print str(v.encode('utf-8'))
            result.append(dict(zip(columns, r)))

        conn.close()
        return  {'rows': result, 'total_page':total_page, 'current_page': current_page, 'total_rows': total_rows}


def bloom_filter_api(filter_type, uri_list =[], uri_size=1000000, err_rate=0.01,):

    if filter_type == 'uri_generator':
        redisdb = 1
        tablename = 'uri_generator'
    elif filter_type == 'uri_parse':
        redisdb = 2
        tablename = 'uri_parse'

    elif filter_type == 'ip':
        redisdb = 3
        tablename = 'ip'
    else :
        redisdb = 4
        tablename = filter_type
    blmfilter = BloomFilter(uri_size, err_rate, redisdb)
    filter_list_unique = []
    filter_list_old = []

    if uri_list == []:
        return filter_list_unique
    else:
        # print uri_list
        for uri in uri_list:
            if blmfilter.add(uri) == True:
                filter_list_old.append(uri)
            else:
                filter_list_unique.append(uri)
        return filter_list_unique
def range_fn(*args):
    if running_python_3:
        return range(*args)
    else:
        return xrange(*args)

def is_string_io(instance):
    if running_python_3:
       return isinstance(instance, BytesIO)
    else:
        return isinstance(instance, (StringIO.StringIO,
                                     cStringIO.InputType,
                                     cStringIO.OutputType))

def make_hashfuncs(num_slices, num_bits):
    if num_bits >= (1 << 31):
        fmt_code, chunk_size = 'Q', 8
    elif num_bits >= (1 << 15):
        fmt_code, chunk_size = 'I', 4
    else:
        fmt_code, chunk_size = 'H', 2
    total_hash_bits = 8 * num_slices * chunk_size
    if total_hash_bits > 384:
        hashfn = hashlib.sha512
    elif total_hash_bits > 256:
        hashfn = hashlib.sha384
    elif total_hash_bits > 160:
        hashfn = hashlib.sha256
    elif total_hash_bits > 128:
        hashfn = hashlib.sha1
    else:
        hashfn = hashlib.md5
    fmt = fmt_code * (hashfn().digest_size // chunk_size)
    num_salts, extra = divmod(num_slices, len(fmt))
    if extra:
        num_salts += 1
    salts = tuple(hashfn(hashfn(pack('I', i)).digest()) for i in range_fn(num_salts))

    def _make_hashfuncs(key):
        if running_python_3:
            if isinstance(key, str):
                key = key.encode('utf-8')
            else:
                key = str(key).encode('utf-8')
        else:
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            else:
                key = str(key)
        i = 0
        for salt in salts:
            h = salt.copy()
            h.update(key)
            for uint in unpack(fmt, h.digest()):
                yield uint % num_bits
                i += 1
                if i >= num_slices:
                    return
    return _make_hashfuncs
class BloomFilter(object):
    FILE_FMT = b'<dQQQQ'

    def __init__(self, capacity, error_rate, redisdb):
        """Implements a space-efficient probabilistic data structure
        capacity
            this BloomFilter must be able to store at least *capacity* elements
            while maintaining no more than *error_rate* chance of false
            positives
        error_rate
            the error_rate of the filter returning false positives. This
            determines the filters capacity. Inserting more than capacity
            elements greatly increases the chance of false positives.

        """
        #print redisdb

        if not (0 < error_rate < 1):
            raise ValueError("Error_Rate must be between 0 and 1.")
        if not capacity > 0:
            raise ValueError("Capacity must be > 0")
        # given M = num_bits, k = num_slices, P = error_rate, n = capacity
        #       k = log2(1/P)
        # solving for m = bits_per_slice
        # n ~= M * ((ln(2) ** 2) / abs(ln(P)))
        # n ~= (k * m) * ((ln(2) ** 2) / abs(ln(P)))
        # m ~= n * abs(ln(P)) / (k * (ln(2) ** 2))
        num_slices = int(math.ceil(math.log(1.0 / error_rate, 2)))
        bits_per_slice = int(math.ceil(
            (capacity * abs(math.log(error_rate))) /
            (num_slices * (math.log(2) ** 2))))





        self._setup(error_rate, num_slices, bits_per_slice, capacity, 0)
        self._rediscontpool(redisdb)
        #self._rediscontpool(redisdb, host='localhost', port= 6379)
        # self.bitarray = bitarray.bitarray(self.num_bits, endian='little')
        # self.bitarray.setall(False)
    """
    def _rediscontpool(self, redisdb, host, port):
        #pool = redis.Redis(host, port, redisdb)
        self.redisdb = redisdb
        self.redispool = redis.StrictRedis(host = 'localhost',port=6379,db= redisdb)
        #self.redispool = redis.StrictRedis(connection_pool=pool)
    """


    def _rediscontpool(self, redisdb):
        #pool = redis.Redis(host, port, redisdb)
        self.redisdb = redisdb
        #self.redispool = redis.StrictRedis(host = 'localhost',port=6379,db= redisdb)
        redisdbstr =str(redisdb)
        redis_url = redis_addr+ '/' + redisdbstr

        self.redispool = redis.StrictRedis.from_url(redis_url)



    def _setup(self, error_rate, num_slices, bits_per_slice, capacity, count):
        self.error_rate = error_rate
        self.num_slices = num_slices
        self.bits_per_slice = bits_per_slice
        self.capacity = capacity
        self.num_bits = num_slices * bits_per_slice
        self.count = count
        self.make_hashes = make_hashfuncs(self.num_slices, self.bits_per_slice)

    def __contains__(self, key):
        """Tests a key's membership in this bloom filter.
        >>> b = BloomFilter(capacity=100)
        >>> b.add("hello")
        False
        >>> "hello" in b
        True
        """
        bits_per_slice = self.bits_per_slice
        # bitarray = self.bitarray
        hashes = self.make_hashes(key)
        offset = 0
        red = self.redispool
        for k in hashes:
            # if not bitarray[offset + k]:
            if not redispool.getbit(self.redisdb, offset + k):
                return False
            offset += bits_per_slice
        return True

    def __len__(self):
        """Return the number of keys stored by this bloom filter."""
        return self.count

    def add(self, key, skip_check=False):
        """ Adds a key to this bloom filter. If the key already exists in this
        filter it will return True. Otherwise False.
        >>> b = BloomFilter(capacity=100)
        >>> b.add("hello")
        False
        >>> b.add("hello")
        True
        >>> b.count
        1
        """
        # bitarray = self.bitarray
        bits_per_slice = self.bits_per_slice
        hashes = self.make_hashes(key)
        found_all_bits = True
        redispool = self.redispool

        redisdb = self.redisdb
        if self.count > self.capacity:
            raise IndexError("BloomFilter is at capacity")
        offset = 0

        for k in hashes:
            ###if not skip_check and found_all_bits and not bitarray[offset + k]
            bit_value = redispool.setbit('uri', offset + k, 1)
            if not skip_check and found_all_bits and not bit_value:
                found_all_bits = False
            # self.bitarray[offset + k] = True
            offset += bits_per_slice

        if skip_check:
            self.count += 1

            return False
        elif not found_all_bits:
            self.count += 1
            return False
        else:
            return True

    def copy(self):
        """Return a copy of this bloom filter.
        """
        new_filter = BloomFilter(self.capacity, self.error_rate)
        new_filter.bitarray = self.bitarray.copy()
        return new_filter

    def union(self, other):
        """ Calculates the union of the two underlying bitarrays and returns
        a new bloom filter object."""
        if self.capacity != other.capacity or \
                        self.error_rate != other.error_rate:
            raise ValueError("Unioning filters requires both filters to have \
both the same capacity and error rate")
        new_bloom = self.copy()
        new_bloom.bitarray = new_bloom.bitarray | other.bitarray
        return new_bloom

    def __or__(self, other):
        return self.union(other)

    def intersection(self, other):
        """ Calculates the intersection of the two underlying bitarrays and returns
        a new bloom filter object."""
        if self.capacity != other.capacity or \
                        self.error_rate != other.error_rate:
            raise ValueError("Intersecting filters requires both filters to \
have equal capacity and error rate")
        new_bloom = self.copy()
        new_bloom.bitarray = new_bloom.bitarray & other.bitarray
        return new_bloom

    def __and__(self, other):
        return self.intersection(other)

    def tofile(self, f):
        """Write the bloom filter to file object `f'. Underlying bits
        are written as machine values. This is much more space
        efficient than pickling the object."""
        f.write(pack(self.FILE_FMT, self.error_rate, self.num_slices,
                     self.bits_per_slice, self.capacity, self.count))
        (f.write(self.bitarray.tobytes()) if is_string_io(f)
         else self.bitarray.tofile(f))

    @classmethod
    def fromfile(cls, f, n=-1):
        """Read a bloom filter from file-object `f' serialized with
        ``BloomFilter.tofile''. If `n' > 0 read only so many bytes."""
        headerlen = calcsize(cls.FILE_FMT)

        if 0 < n < headerlen:
            raise ValueError('n too small!')

        filter = cls(1)  # Bogus instantiation, we will `_setup'.
        filter._setup(*unpack(cls.FILE_FMT, f.read(headerlen)))
        filter.bitarray = bitarray.bitarray(endian='little')
        if n > 0:
            (filter.bitarray.frombytes(f.read(n - headerlen)) if is_string_io(f)
             else filter.bitarray.fromfile(f, n - headerlen))
        else:
            (filter.bitarray.frombytes(f.read()) if is_string_io(f)
             else filter.bitarray.fromfile(f))
        if filter.num_bits != filter.bitarray.length() and \
                (filter.num_bits + (8 - filter.num_bits % 8)
                     != filter.bitarray.length()):
            raise ValueError('Bit length mismatch!')

        return filter

    def __getstate__(self):
        d = self.__dict__.copy()
        del d['make_hashes']
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
        self.make_hashes = make_hashfuncs(self.num_slices, self.bits_per_slice)


class ScalableBloomFilter(object):
    SMALL_SET_GROWTH = 2  # slower, but takes up less memory
    LARGE_SET_GROWTH = 4  # faster, but takes up more memory faster
    FILE_FMT = '<idQd'

    def __init__(self, initial_capacity=100, error_rate=0.001,
                 mode=SMALL_SET_GROWTH):
        """Implements a space-efficient probabilistic data structure that
        grows as more items are added while maintaining a steady false
        positive rate
        initial_capacity
            the initial capacity of the filter
        error_rate
            the error_rate of the filter returning false positives. This
            determines the filters capacity. Going over capacity greatly
            increases the chance of false positives.
        mode
            can be either ScalableBloomFilter.SMALL_SET_GROWTH or
            ScalableBloomFilter.LARGE_SET_GROWTH. SMALL_SET_GROWTH is slower
            but uses less memory. LARGE_SET_GROWTH is faster but consumes
            memory faster.
        >>> b = ScalableBloomFilter(initial_capacity=512, error_rate=0.001, \
                                    mode=ScalableBloomFilter.SMALL_SET_GROWTH)
        >>> b.add("test")
        False
        >>> "test" in b
        True
        >>> unicode_string = u'Â¡'
        >>> b.add(unicode_string)
        False
        >>> unicode_string in b
        True
        """
        if not error_rate or error_rate < 0:
            raise ValueError("Error_Rate must be a decimal less than 0.")
        self._setup(mode, 0.9, initial_capacity, error_rate)
        self.filters = []

    def _setup(self, mode, ratio, initial_capacity, error_rate):
        self.scale = mode
        self.ratio = ratio
        self.initial_capacity = initial_capacity
        self.error_rate = error_rate

    def __contains__(self, key):
        """Tests a key's membership in this bloom filter.
        >>> b = ScalableBloomFilter(initial_capacity=100, error_rate=0.001, \
                                    mode=ScalableBloomFilter.SMALL_SET_GROWTH)
        >>> b.add("hello")
        False
        >>> "hello" in b
        True
        """
        for f in reversed(self.filters):
            if key in f:
                return True
        return False

    def add(self, key):
        """Adds a key to this bloom filter.
        If the key already exists in this filter it will return True.
        Otherwise False.
        >>> b = ScalableBloomFilter(initial_capacity=100, error_rate=0.001, \
                                    mode=ScalableBloomFilter.SMALL_SET_GROWTH)
        >>> b.add("hello")
        False
        >>> b.add("hello")
        True
        """
        if key in self:
            return True
        if not self.filters:
            filter = BloomFilter(
                capacity=self.initial_capacity,
                error_rate=self.error_rate * (1.0 - self.ratio))
            self.filters.append(filter)
        else:
            filter = self.filters[-1]
            if filter.count >= filter.capacity:
                filter = BloomFilter(
                    capacity=filter.capacity * self.scale,
                    error_rate=filter.error_rate * self.ratio)
                self.filters.append(filter)
        filter.add(key, skip_check=True)
        return False

    @property
    def capacity(self):
        """Returns the total capacity for all filters in this SBF"""
        return sum(f.capacity for f in self.filters)

    @property
    def count(self):
        return len(self)

    def tofile(self, f):
        """Serialize this ScalableBloomFilter into the file-object
        `f'."""
        f.write(pack(self.FILE_FMT, self.scale, self.ratio,
                     self.initial_capacity, self.error_rate))

        # Write #-of-filters
        f.write(pack(b'<l', len(self.filters)))

        if len(self.filters) > 0:
            # Then each filter directly, with a header describing
            # their lengths.
            headerpos = f.tell()
            headerfmt = b'<' + b'Q' * (len(self.filters))
            f.write(b'.' * calcsize(headerfmt))
            filter_sizes = []
            for filter in self.filters:
                begin = f.tell()
                filter.tofile(f)
                filter_sizes.append(f.tell() - begin)

            f.seek(headerpos)
            f.write(pack(headerfmt, *filter_sizes))

    @classmethod
    def fromfile(cls, f):
        """Deserialize the ScalableBloomFilter in file object `f'."""
        filter = cls()
        filter._setup(*unpack(cls.FILE_FMT, f.read(calcsize(cls.FILE_FMT))))
        nfilters, = unpack(b'<l', f.read(calcsize(b'<l')))
        if nfilters > 0:
            header_fmt = b'<' + b'Q' * nfilters
            bytes = f.read(calcsize(header_fmt))
            filter_lengths = unpack(header_fmt, bytes)
            for fl in filter_lengths:
                filter.filters.append(BloomFilter.fromfile(f, fl))
        else:
            filter.filters = []

        return filter

    def __len__(self):
        """Returns the total number of elements stored in this SBF"""
        return sum(f.count for f in self.filters)


"""              """
class GeneratorTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    # @unittest.skip("skipping read from file")
    def test_obtain_enterprises(self):
        self.generator = Generator()
        self.generator.obtain_enterprises()
        for name in self.generator.enterprises:
            logging.debug("enterprise name is %s."%(name))

        self.assertGreater(len(self.generator.enterprises), 0)

    @unittest.skip("skipping read from file")
    def test_obtain_urls(self):
        self.generator = Generator()
        self.generator.search_url_with_batch()

        for uri in self.generator.uris:
            logging.debug("urls is %s", uri)
        logging.debug("urls count is %d", len(self.generator.uris))

        self.assertGreater(len(self.generator.uris), 0)

    @unittest.skip("skipping read from file")
    def test_mysql(self):
        generator = Generator()
        result = generator.paginate(0, 10)
        print result


    @unittest.skip("skipping read from file")
    def test_generator_over_totalpage(self):
        generator = Generator()
        conn = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db='clawer', charset='utf8', port=PORT)
        sql='select count(*) from enterprise_enterprise where slice = %d'%(SLICE)
        cur = conn.cursor()
        count = cur.execute(sql)
        total_rows = cur.fetchone()[0]
        total_page = total_rows/10

        result = generator.paginate(total_page+1, 10)
        print result
        self.assertEqual(result['current_page'], 0)



if __name__ == "__main__":

    if DEBUG:  # 如果DEBUG为True则进入测试单元
        unittest.main()
    else:
        generator = Generator()
        generator.search_url_with_batch()

        for uri in generator.uris:
            # str_uri = str(uri.encode("utf-8")).split(" ")
            str_uri = uri.encode("utf-8").split(" ")
            print json.dumps({"uri": str_uri[0], "args": str_uri[1]})
