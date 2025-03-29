from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import logging
import random
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
import redis
import os
import smtplib
from email.mime.text import MIMEText
# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('guba_browser.log'), logging.StreamHandler()]
)

class BrowserCrawler:
    """基于浏览器自动化的股吧评论采集器"""
    
    def __init__(self, headless=True):
        # 初始化浏览器配置
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument(f'--user-agent={self._random_user_agent()}')
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.implicitly_wait(10)
        
        # Redis连接配置
        self.redis = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        self.last_id_key = 'guba:last_post_id'
        
    def _random_user_agent(self):
        """生成随机用户代理"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1'
        ]
        return random.choice(agents)

    def _human_like_behavior(self):
        """模拟人类操作行为"""
        self.driver.execute_script("window.scrollBy(0, 500)")
        time.sleep(random.uniform(1.5, 3.0))
        
    def get_comments(self, stock_code='600519', max_pages=3):
        """获取股吧评论数据（带增量采集功能）"""
        comments = []
        last_id = self.redis.get(self.last_id_key) or '1533853127'  # 从Redis获取最后采集ID
        base_url = f'https://guba.eastmoney.com/news,{stock_code},{last_id}.html'
        
        # 代理设置（根据实际情况配置）
        # self.options.add_argument('--proxy-server=http://user:pass@ip:port')
        try:
            self.driver.get(base_url)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.articleh'))
            )

            for page in range(1, max_pages+1):
                # 解析当前页数据
                items = self.driver.find_elements(By.CSS_SELECTOR, '.articleh')
                for item in items:
                    try:
                        comment = {
                            '发布时间': item.find_element(By.CSS_SELECTOR, '.l5').text,
                            '标题': item.find_element(By.CSS_SELECTOR, '.l3 a').text,
                            '阅读量': item.find_element(By.CSS_SELECTOR, '.l1').text,
                            '评论数': item.find_element(By.CSS_SELECTOR, '.l2').text,
                            '作者': item.find_element(By.CSS_SELECTOR, '.l4').text
                        }
                        comments.append(comment)
                    except Exception as e:
                        logging.warning(f"解析异常: {str(e)}")

                logging.info(f"第{page}页采集完成，获得{len(comments)}条数据")
                
                # 翻页操作（修复括号和缩进）
                if page < max_pages:
                    next_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '.pagenext'))
                    )
                    self.driver.execute_script("arguments[0].click();", next_btn)
                    time.sleep(random.uniform(3, 5))
                    self._human_like_behavior()

        except Exception as e:
            logging.error(f"采集过程中断: {str(e)}")
            self._send_alert_email(str(e))
        finally:
            self.driver.quit()
            # 更新最后采集ID
            if comments:
                latest_id = comments[-1].get('帖子ID', last_id)
                self.redis.set(self.last_id_key, latest_id)
        
        return pd.DataFrame(comments)

    def _send_alert_email(self, error_msg):
        """发送异常告警邮件"""
        msg = MIMEText(f"爬虫异常告警：\n{error_msg}\n\n请及时处理！")
        msg['Subject'] = '股吧爬虫异常告警'
        msg['From'] = 'crawler@example.com'
        msg['To'] = 'admin@example.com'
        
        try:
            with smtplib.SMTP('smtp.example.com', 587) as server:
                server.starttls()
                server.login('user', 'pass')
                server.send_message(msg)
            logging.info("告警邮件已发送")
        except Exception as e:
            logging.error(f"邮件发送失败: {str(e)}")

    def save_data(self, df):
        """保存数据到CSV（按股票代码分目录存储）"""
        if not df.empty:
            stock_code = df.iloc[0].get('股票代码', 'unknown')
            os.makedirs(f'data/{stock_code}', exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f'data/{stock_code}/guba_{stock_code}_{timestamp}.csv'
            df.to_csv(filename, index=False, encoding='utf_8_sig')
            logging.info(f"数据已保存至 {filename}")
            return True
        return False

if __name__ == '__main__':
    # 创建定时任务调度器
    scheduler = BlockingScheduler()
    scheduler.add_job(
        func=lambda: BrowserCrawler().get_comments(max_pages=3),
        trigger=IntervalTrigger(minutes=15),
        max_instances=1
    )

    try:
        logging.info("爬虫定时任务已启动，每15分钟执行一次")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("爬虫定时任务已正常停止")