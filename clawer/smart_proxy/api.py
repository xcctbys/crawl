#coding:utf8
import os
import sys
sys.path.append(os.getcwd())

from smart_proxy.models import ProxyIp
# from models import ProxyIp


class Proxy(object):
    def __init__(self):
        pass

    def get_proxy(self, num=5, province=None, is_valid=True):
        print province
        if province:
            ip_list = ProxyIp.objects.filter(province__icontains=province, is_valid=is_valid)
            ip_list = [item.ip_port for item in ip_list]
            # print ip_list
        else:
            # print ProxyIp.objects.filter(is_valid=True)
            ip_list = ProxyIp.objects.filter(is_valid=is_valid)
            ip_list = [item.ip_port for item in ip_list]

        if len(ip_list) < num:
            temp_list = ProxyIp.objects.filter(province__icontains='OTHER', is_valid=is_valid)
            temp_list = [item.ip_port for item in temp_list]
            ip_list.extend(temp_list)
        if len(ip_list) <= num:
            return ip_list
        else:
            return ip_list[:num]

if __name__ == '__main__':
    proxy = Proxy()
    print proxy.get_proxy()