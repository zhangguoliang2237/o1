import requests
import pandas as pd
import time
import json

def get_eastmoney_stock_data(stock_code='600519', start_date='20200101', end_date='20250326'):
    """
    从东方财富API获取股票历史数据
    参数：
    stock_code - 股票代码(沪市前加1，深市前加0)
    start_date - 开始日期(YYYYMMDD)
    end_date - 结束日期(YYYYMMDD)
    """
    # 构造请求URL
    url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
    
    # 请求参数
    params = {
        'secid': f"{'1' if stock_code.startswith('6') else '0'}.{stock_code}",
        'ut': '7eea3edcaed734bea9cbfc24409ed989',
        'fields1': 'f1,f2,f3,f4,f5,f6',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
        'klt': '101',  # 日k线
        'fqt': '1',     # 复权类型
        'beg': start_date,
        'end': end_date,
        'lmt': '100000', # 最大数据量
        '_': int(time.time() * 1000)
    }
    
    try:
        print(f"正在获取 {stock_code} 的历史数据...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data['data'] is None:
            print("未获取到数据，请检查股票代码和日期范围")
            return False
            
        # 解析数据
        klines = data['data']['klines']
        result = []
        for item in klines:
            fields = item.split(',')
            result.append({
                '日期': fields[0],
                '开盘': float(fields[1]),
                '收盘': float(fields[2]),
                '最高': float(fields[3]),
                '最低': float(fields[4]),
                '成交量(手)': int(fields[5]),
                '成交额(元)': float(fields[6]),
                '振幅': float(fields[7]),
                '涨跌幅': float(fields[8]),
                '涨跌额': float(fields[9]),
                '换手率': float(fields[10])
            })
        
        # 保存为CSV
        df = pd.DataFrame(result)
        filename = f'stock_{stock_code}_{start_date}_{end_date}.csv'
        df.to_csv(filename, index=False, encoding='utf_8_sig')
        print(f"成功保存数据到 {filename}")
        return True
        
    except Exception as e:
        print(f"获取数据失败: {str(e)}")
        return False

if __name__ == '__main__':
    # 示例：获取贵州茅台(600519)2020年至今的数据
    get_eastmoney_stock_data('600519', '20200101', '20250326')