import requests
from bs4 import BeautifulSoup
import csv
import time
import argparse
import datetime

# 设置请求头模拟浏览器访问
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def get_stock_data(start_date: str = '20250301', end_date: str = '20250326'):
    url = 'http://quote.eastmoney.com/center/gridlist.html#hs_a_board'
    
    # 请求头变量重命名避免冲突
    request_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'http://quote.eastmoney.com/',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': 'qgqp_b_id=3b4816d9f7b3a3a1a3a3a3a3a3a3a3a; em_hq_fls=js'
    }
    
    try:
        # 使用东方财富API接口直接获取JSON数据
        api_url = 'http://push2.eastmoney.com/api/qt/clist/get'
        params = {
            'pn': 1,
            'pz': 10000,  # 最大允许值
            'po': 1,
            'np': 1,
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fs': 'm:0 t:6,m:0 t:13,m:0 t:80,m:1 t:2,m:1 t:23',  # 包含所有市场
            'fields': 'f12,f14,f2,f3,f4,f5,f6,f7,f15,f16,f17,f18,f124',
            'beg': start_date.replace('-', ''),  # 格式化日期
            'end': end_date.replace('-', ''),
            '_': int(time.time() * 1000)
        }
        
        # 添加重试机制
        for attempt in range(3):
            try:
                response = requests.get(api_url, headers=request_headers, params=params, timeout=10)
                response.encoding = 'utf-8'
                data = response.json()
                
                # 解析JSON数据
                stock_list = data.get('data', {}).get('diff', [])
                if not stock_list:
                    print("未获取到有效数据，响应内容：", data)
                    return [], []
                print(f"获取到 {len(stock_list)} 条数据,stock_list:{stock_list}")
                # 定义字段映射（中文表头）
                columns = [
                    '代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量(手)',
                    '成交额', '振幅', '最高', '最低', '今开', '昨收'
                ]
                
                # 提取数据行
                rows = []
                for stock in stock_list:
                    row = [
                        stock.get('f12', ''),  # 代码
                        stock.get('f14', ''),  # 名称
                        stock.get('f2', ''),   # 最新价
                        f"{stock.get('f3', '')}%",  # 涨跌幅
                        stock.get('f4', ''),   # 涨跌额
                        stock.get('f5', ''),   # 成交量(手)
                        stock.get('f6', ''),   # 成交额
                        f"{stock.get('f7', '')}%",  # 振幅
                        stock.get('f15', ''),  # 最高
                        stock.get('f16', ''),  # 最低
                        stock.get('f17', ''),  # 今开
                        stock.get('f18', '')   # 昨收
                    ]
                    rows.append(row)
                    
                return columns, rows
                
            except requests.exceptions.RequestException as e:
                print(f"请求失败，尝试 {attempt+1}/3: {str(e)}")
                time.sleep(2)
        
        print("多次尝试后仍失败")
        return [], []
        
    except Exception as e:
        print(f"数据获取失败: {str(e)}")
        return [], []

def save_to_csv(filename, headers, data):
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        print(f"数据已保存到 {filename}")
    except Exception as e:
        print(f"文件保存失败: {str(e)}")

if __name__ == "__main__":
    # 添加命令行参数解析
    parser = argparse.ArgumentParser(description='东方财富股票数据下载工具')
    parser.add_argument('-s', '--start', type=str, default='2025-03-01',
                       help='开始日期（格式：YYYY-MM-DD）')
    parser.add_argument('-e', '--end', type=str, default=time.strftime("%Y-%m-%d"),
                       help='结束日期（格式：YYYY-MM-DD）')
    parser.add_argument('-o', '--output', type=str,
                       help='输出文件名，默认格式：stock_data_起止日期.csv')
    
    args = parser.parse_args()
    
    # 验证日期格式
    try:
        datetime.datetime.strptime(args.start, "%Y-%m-%d")
        datetime.datetime.strptime(args.end, "%Y-%m-%d")
    except ValueError:
        print("错误：日期格式应为YYYY-MM-DD")
        exit(1)
    
    # 生成文件名
    if not args.output:
        args.output = f'stock_data_{args.start.replace("-","")}-{args.end.replace("-","")}.csv'
    
    # 获取数据并保存
    headers, data = get_stock_data(args.start, args.end)
    if data:
        save_to_csv(args.output, headers, data)
        print(f"成功保存 {len(data)} 条记录到 {args.output}")
    else:
        print("没有获取到有效数据")