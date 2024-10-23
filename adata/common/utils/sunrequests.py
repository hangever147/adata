# -*- coding: utf-8 -*-
"""
代理:https://jahttp.zhimaruanjian.com/getapi/

@desc: adata 请求工具类
@author: 1nchaos
@time:2023/3/30
@log: 封装请求次数
"""

import threading
import time

import requests
import socks
import socket
from requests.exceptions import RequestException
from urllib3.exceptions import NewConnectionError

class SunProxy(object):
    _data = {}
    _instance_lock = threading.Lock()

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(SunProxy, "_instance"):
            with SunProxy._instance_lock:
                if not hasattr(SunProxy, "_instance"):
                    SunProxy._instance = object.__new__(cls)

    @classmethod
    def set(cls, key, value):
        cls._data[key] = value

    @classmethod
    def get(cls, key):
        return cls._data.get(key)

    @classmethod
    def delete(cls, key):
        if key in cls._data:
            del cls._data[key]


class SunRequests(object):
    def __init__(self, sun_proxy: SunProxy = None) -> None:
        super().__init__()
        self.sun_proxy = sun_proxy

    def request(self, method='get', url=None, times=3, retry_wait_time=1588, proxies=None, wait_time=None, **kwargs):
        """
        简单封装的请求，参考requests，增加循环次数和次数之间的等待时间
        :param proxies: 代理配置，支持 HTTP 和 SOCKS5
        :param method: 请求方法： get；post
        :param url: 请求的 URL
        :param times: 重试次数，默认 3 次
        :param retry_wait_time: 重试之间的等待时间，毫秒
        :param wait_time: 请求之间的等待时间，毫秒
        :param kwargs: 其它 requests 参数
        :return: res
        """
        # 1. 获取代理配置
        proxies = self.__get_proxies(proxies)

        # 2. 执行请求
        res = None
        for i in range(times):
            if wait_time:
                time.sleep(wait_time / 1000)  # 请求之间的等待

            try:
                res = requests.request(method=method, url=url, proxies=proxies, **kwargs)
                if res.status_code in (200, 404):
                    return res
            except (RequestException, NewConnectionError) as e:
                print(f"Request failed: {e}")

            time.sleep(retry_wait_time / 1000)  # 重试之间的等待时间

        return res

    def __get_proxies(self, proxies):
        """
        获取代理配置，支持 HTTP 和 SOCKS5
        """
        if proxies is None:
            proxies = {}

        is_proxy = SunProxy.get('is_proxy')
        ip = SunProxy.get('ip')
        proxy_url = SunProxy.get('proxy_url')
        proxy_type = SunProxy.get('proxy_type', 'http')  # 默认 HTTP 代理，如果未设置类型
        socks5_proxy = SunProxy.get('socks5_proxy')

        # 如果是 SOCKS5 代理
        if proxy_type == 'socks5' and socks5_proxy:
            proxies = {
                'http': f'{socks5_proxy}',
                'https': f'{socks5_proxy}',
            }
        # 如果是 HTTP/HTTPS 代理
        elif not ip and is_proxy and proxy_url:
            ip = requests.get(url=proxy_url).text.strip()
            if is_proxy and ip:
                proxies = {'https': f"http://{ip}", 'http': f"http://{ip}"}

        return proxies
sun_requests = SunRequests()
