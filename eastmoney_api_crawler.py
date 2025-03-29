import requests
import pandas as pd
import time
import json
import random
from datetime import datetime

class EastmoneyGubaCrawler:
    """东方财富股吧评论爬虫"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://guba.eastmoney.com/'
        }
        self.base_url = "https://guba.eastmoney.com/list,{stock_code}_{page}.html"
        
        # API参数配置
        self.api_params = {
            'cb': 'jQuery11240904396623880852_',
            'pn': 1,  # 页码
            'np': 1,
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fields': 'f12,f14,f62,f128,f136,f124,f120,f121',
            '_': int(time.time() * 1000)
        }
    
    def get_comments(self, stock_code='600519', start_time=None, end_time=None, max_pages=5):
        """
        获取股票评论数据
        :param stock_code: 股票代码（6位数字）
        :param start_time: 起始时间（格式：YYYY-MM-DD）
        :param end_time: 结束时间
        :param max_pages: 最大爬取页数
        :return: DataFrame格式的评论数据
        """
        comments = []
        
        for page in range(1, max_pages+1):
            try:
                # 构造动态参数
                params = self.api_params.copy()
                params.update({
                    'secid': f'1.{stock_code}',
                    'pn': page,
                    '_': int(time.time() * 1000)
                })
                
                # 添加时间过滤
                if start_time:
                    params['beg'] = datetime.strptime(start_time, '%Y-%m-%d').timestamp()
                if end_time:
                    params['end'] = datetime.strptime(end_time, '%Y-%m-%d').timestamp()
                
                # 发送API请求
                api_url = "http://guba.eastmoney.com/interface/GetData.aspx"
                response = requests.get(
                    url=api_url,
                    params=params,
                    headers=self.headers,
                    timeout=10
                )
                response.raise_for_status()
                
                # 解析JSON数据
                json_str = response.text[response.text.find('{'):-1]
                data = json.loads(json_str)
                
                # 提取评论数据
                for item in data.get('re', []):
                    comment = {
                        '股票代码': stock_code,
                        '发布时间': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['publish_time'])),
