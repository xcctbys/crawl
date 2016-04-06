#coding:utf8
from models import ProxyIp

class RoundProxy(object):
    def __init__(self):
        pass
    def change_valid(self, id):
        proxy = ProxyIp()
        one_ip = proxy.object.filter(id=id) #得到对应id的代理。
        one_ip = {'http':'http://'+ one_ip}
        try:
            resp = reqst.get(url, proxies=proxy)
        except:
            update_data(id, flag=False) #更新，置为不可用。
            return False
        if resp.status_code == 200:
            return True
        update_data(id, falg=False)
        return False
    def run(self):
        total_count = proxy.object.all().count() #获得数据库里数量
        #pool.map(test_OK, range(1, total_count))
        for id in range(1, total_count):
            self.change_vaild(id)
        if total_count > setting.MAX_PROXY_NUM:
            delete_data(setting.MAX_PROXY_NUM - total_count)#删除多余无效数据