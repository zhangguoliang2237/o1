import os
import requests
import pandas as pd
import time
from datetime import datetime

def get_eastmoney_stock_data(stock_code='600519', start_date='20200101', end_date=None):
    """
    从东方财富API获取股票历史行情数据并保存到data目录
    
    参数：
    stock_code - 6位股票代码(例如：'600519'茅台)
    start_date - 起始日期(格式：YYYYMMDD)
    end_date   - 结束日期(默认当前日期)
    """
    # 创建data目录
    os.makedirs('data', exist_ok=True)
    
    # 设置默认结束日期为今天
    end_date = end_date or datetime.now().strftime("%Y%m%d")
    
    # 验证股票代码
    if len(stock_code) != 6 or not stock_code.isdigit():
        raise ValueError("股票代码必须为6位数字")
    
    # 构造请求参数
    url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        'secid': f"{'1' if stock_code.startswith('6') else '0'}.{stock_code}",
        'ut': '7eea3edcaed734bea9cbfc24409ed989',
        'fields1': 'f1,f2,f3,f4,f5,f6',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
        'klt': '101',  # 日k线
        'fqt': '1',     # 前复权
        'beg': start_date,
        'end': end_date,
        'lmt': '100000',
        '_': int(time.time() * 1000)
    }
    
    try:
        print(f"正在获取 {stock_code} [{start_date}-{end_date}] 历史数据...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data['data'] is None:
            print(f"未获取到数据，请检查股票代码 {stock_code} 是否存在")
            return False
            
        # 解析数据
        klines = data['data']['klines']
        if not klines:
            print("该时间范围内无可用数据")
            return False
            
        # 转换为DataFrame
        df = pd.DataFrame([parse_kline_item(item) for item in klines])
        
        # 保存文件
        filename = f"data/stock_{stock_code}_{start_date}_{end_date}.csv"
        df.to_csv(filename, index=False, encoding='utf_8_sig')
        print(f"数据已保存至 {filename}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {str(e)}")
    except Exception as e:
        print(f"数据处理出错: {str(e)}")
    return False

def parse_kline_item(item):
    """解析单条K线数据"""
    fields = item.split(',')
    return {
        '日期': fields[0],
        '开盘价': float(fields[1]),
        '收盘价': float(fields[2]),
        '最高价': float(fields[3]),
        '最低价': float(fields[4]),
        '成交量(手)': int(fields[5]),
        '成交额(元)': float(fields[6]),
        '振幅(%)': float(fields[7]),
        '涨跌幅(%)': float(fields[8]),
        '涨跌额': float(fields[9]),
        '换手率(%)': float(fields[10]),
    }

if __name__ == '__main__':
    # 示例用法
    get_eastmoney_stock_data('600519', '20200101')  # 茅台
    get_eastmoney_stock_data('300750', '20230101')  # 宁德时代