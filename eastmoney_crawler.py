from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

def get_eastmoney_stock_history(stock_code='600519', start_date='2020-01-01', end_date='2025-03-26'):
    # 设置Chrome选项
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 无头模式
    
    # 自动管理ChromeDriver
    driver = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager().install()), options=options)
    
    try:
        # 访问股票历史行情页面
        driver.get(f'http://quote.eastmoney.com/concept/{stock_code}.html#kline')
        
        # 等待页面加载完成
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.kline-container')))
        
        # 执行JavaScript设置日期并点击查询
        driver.execute_script(f"""
            document.querySelector('input[placeholder="开始日期"]').value = '{start_date}';
            document.querySelector('input[placeholder="结束日期"]').value = '{end_date}';
            document.querySelector('.toolbar-search-button').click();
        """)
        time.sleep(3)
        
        all_data = []
        while True:
            # 获取表格数据
            table = driver.find_element(By.CLASS_NAME, 'history-table')
            df = pd.read_html(table.get_attribute('outerHTML'))[0]
            all_data.append(df)
            
            # 尝试翻页
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, '.next-btn:not(.disabled)')
                next_btn.click()
                time.sleep(2)
            except:
                break
                
        # 合并数据并保存
        final_df = pd.concat(all_data)
        final_df.to_csv(f'stock_history_eastmoney.csv', index=False)
        print(f'成功保存{len(final_df)}条数据')
        
    finally:
        driver.quit()

if __name__ == '__main__':
    get_eastmoney_stock_history()