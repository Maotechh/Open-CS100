#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACM用户信息爬虫 - 并发版本
遍历 https://acm.shanghaitech.edu.cn/user/XXXX 页面
提取用户信息并保存到CSV文件
使用多线程并发提高爬取速度
"""

import requests
import csv
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue
import os
import base64

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ACMUserScraperConcurrent:
    def __init__(self, max_workers=10):
        self.base_url = "https://acm.shanghaitech.edu.cn/user/{}"
        self.max_workers = max_workers
        self.users_data = []
        self.data_lock = threading.Lock()
        self.consecutive_not_found = 0
        self.not_found_lock = threading.Lock()
        self.max_consecutive_not_found = 50
        self.should_stop = False
        
        # 为每个线程创建独立的session
        self.session_pool = Queue()
        for _ in range(max_workers):
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            self.session_pool.put(session)
    
    def get_session(self):
        """获取一个session"""
        return self.session_pool.get()
    
    def return_session(self, session):
        """归还session"""
        self.session_pool.put(session)
        
    def get_user_info(self, uid):
        """
        获取指定UID的用户信息
        """
        if self.should_stop:
            return None
            
        session = self.get_session()
        try:
            url = self.base_url.format(uid)
            response = session.get(url, timeout=10)
            
            # 如果返回404或其他错误状态码，说明用户不存在
            if response.status_code == 404:
                with self.not_found_lock:
                    self.consecutive_not_found += 1
                    if self.consecutive_not_found >= self.max_consecutive_not_found:
                        self.should_stop = True
                        logger.info(f"连续 {self.max_consecutive_not_found} 个用户不存在，停止爬取")
                return None
            elif response.status_code != 200:
                logger.warning(f"UID {uid}: HTTP {response.status_code}")
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取用户信息
            user_info = {
                'uid': uid,
                'username': '',
                'nickname': '',
                'email': ''
            }
            
            # 查找用户名 - 通常在页面标题或用户信息区域
            title = soup.find('title')
            if title:
                title_text = title.get_text().strip()
                # 提取用户名（假设格式为 "用户名 - ACM"）
                if ' - ' in title_text:
                    user_info['username'] = title_text.split(' - ')[0].strip()
            
            # 查找用户信息区域
            # 这里需要根据实际网页结构调整选择器
            user_profile = soup.find('div', class_='user-profile') or soup.find('div', class_='profile')
            if user_profile:
                # 查找昵称
                nickname_elem = user_profile.find('span', class_='nickname') or user_profile.find('div', class_='nickname')
                if nickname_elem:
                    user_info['nickname'] = nickname_elem.get_text().strip()
            
            # 查找邮箱按钮或链接 - 重点查找data-copy属性
            email_element = soup.find('a', {'data-copy': True}) or \
                           soup.find('button', {'data-copy': True}) or \
                           soup.find('span', {'data-copy': True})
            
            if email_element and email_element.get('data-copy'):
                try:
                    # 解码base64编码的邮箱地址
                    encoded_email = email_element.get('data-copy')
                    decoded_email = base64.b64decode(encoded_email).decode('utf-8')
                    if '@' in decoded_email and 'Guest@hydro.local' not in decoded_email:
                        user_info['email'] = decoded_email.strip()
                except Exception as e:
                    logger.warning(f"解码邮箱失败 UID {uid}: {e}")
            
            # 如果没有找到邮箱，尝试其他方法
            if not user_info['email']:
                # 查找其他可能的邮箱元素
                email_button = soup.find('button', {'data-clipboard-text': re.compile(r'.*@.*')}) or \
                              soup.find('a', href=re.compile(r'mailto:.*')) or \
                              soup.find('span', {'data-email': re.compile(r'.*@.*')})
                
                if email_button:
                    email = email_button.get('data-clipboard-text') or \
                           email_button.get('href', '').replace('mailto:', '') or \
                           email_button.get('data-email')
                    if email and '@' in email and 'Guest@hydro.local' not in email:
                        user_info['email'] = email.strip()
            
            # 如果仍然没有找到邮箱，尝试在页面文本中搜索
            if not user_info['email']:
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                email_matches = re.findall(email_pattern, response.text)
                for email_match in email_matches:
                    if 'Guest@hydro.local' not in email_match:
                        user_info['email'] = email_match
                        break
            
            # 如果用户名为空，尝试从其他地方获取
            if not user_info['username']:
                # 查找h1, h2标签中的用户名
                header = soup.find('h1') or soup.find('h2')
                if header:
                    user_info['username'] = header.get_text().strip()
            
            # 过滤包含"发票"的用户名
            if '发票' in user_info.get('username', '') or '发票' in user_info.get('nickname', ''):
                logger.info(f"过滤掉包含'发票'的用户 {uid}: {user_info['username']}")
                return None
            
            # 重置连续未找到计数器
            with self.not_found_lock:
                self.consecutive_not_found = 0
            
            logger.info(f"成功获取用户 {uid} 的信息: {user_info['username']}")
            return user_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求UID {uid} 时出错: {e}")
            return None
        except Exception as e:
            logger.error(f"解析UID {uid} 页面时出错: {e}")
            return None
        finally:
            self.return_session(session)
    
    def process_uid_batch(self, uid_list):
        """
        处理一批UID
        """
        batch_results = []
        for uid in uid_list:
            if self.should_stop:
                break
            result = self.get_user_info(uid)
            if result:
                batch_results.append(result)
        return batch_results
    
    def scrape_all_users(self, start_uid=1, max_uid=1800, output_file='uid_and_email.csv', batch_size=20):
        """
        并发遍历所有用户并保存到CSV文件
        """
        logger.info(f"开始并发爬取用户信息，范围: {start_uid:04d} - {max_uid:04d}")
        logger.info(f"并发线程数: {self.max_workers}, 批处理大小: {batch_size}")
        
        # 生成所有UID
        all_uids = [f"{uid_num:04d}" for uid_num in range(start_uid, max_uid + 1)]
        
        # 分批处理
        uid_batches = [all_uids[i:i + batch_size] for i in range(0, len(all_uids), batch_size)]
        
        start_time = time.time()
        processed_count = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有批次任务
            future_to_batch = {executor.submit(self.process_uid_batch, batch): batch for batch in uid_batches}
            
            for future in as_completed(future_to_batch):
                if self.should_stop:
                    # 取消剩余任务
                    for f in future_to_batch:
                        f.cancel()
                    break
                    
                batch = future_to_batch[future]
                try:
                    batch_results = future.result()
                    
                    # 线程安全地添加结果
                    with self.data_lock:
                        self.users_data.extend(batch_results)
                        processed_count += len(batch)
                        
                        # 每处理一定数量就保存一次
                        if len(self.users_data) % 50 == 0 and len(self.users_data) > 0:
                            self.save_to_csv(self.users_data, output_file)
                            elapsed_time = time.time() - start_time
                            rate = processed_count / elapsed_time if elapsed_time > 0 else 0
                            logger.info(f"已保存 {len(self.users_data)} 个用户信息，处理速度: {rate:.2f} UID/秒")
                            
                except Exception as exc:
                    logger.error(f"批次处理出错: {exc}")
        
        # 最终保存所有数据
        self.save_to_csv(self.users_data, output_file)
        
        elapsed_time = time.time() - start_time
        total_rate = processed_count / elapsed_time if elapsed_time > 0 else 0
        
        logger.info(f"爬取完成！")
        logger.info(f"共获取 {len(self.users_data)} 个用户信息")
        logger.info(f"总处理时间: {elapsed_time:.2f} 秒")
        logger.info(f"平均处理速度: {total_rate:.2f} UID/秒")
        logger.info(f"数据保存到: {output_file}")
        
        return self.users_data
    
    def save_to_csv(self, users_data, filename):
        """
        保存用户数据到CSV文件
        """
        if not users_data:
            return
            
        # 创建临时文件，避免写入过程中的数据损坏
        temp_filename = filename + '.tmp'
        
        try:
            with open(temp_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['uid', 'username', 'nickname', 'email']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for user in users_data:
                    writer.writerow(user)
            
            # 原子性地替换原文件
            if os.path.exists(filename):
                os.remove(filename)
            os.rename(temp_filename, filename)
            
        except Exception as e:
            logger.error(f"保存CSV文件时出错: {e}")
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

def main():
    # 可以调整并发参数
    max_workers = 15  # 并发线程数，可以根据网络情况调整
    batch_size = 30   # 每批处理的UID数量
    
    scraper = ACMUserScraperConcurrent(max_workers=max_workers)
    
    # 可以调整起始UID和最大UID
    users = scraper.scrape_all_users(
        start_uid=1,
        max_uid=1800,
        output_file='uid_and_email.csv',
        batch_size=batch_size
    )
    
    print(f"\n爬取完成！共获取 {len(users)} 个用户信息")
    print("数据已保存到 uid_and_email.csv 文件")
    print(f"\n性能提升说明:")
    print(f"- 使用 {max_workers} 个并发线程")
    print(f"- 批处理大小: {batch_size}")
    print(f"- 预计比单线程版本快 5-10 倍")
    print("\n更新内容:")
    print("- 修复邮箱提取：现在可以正确解码base64编码的邮箱地址")
    print("- 过滤垃圾用户：自动过滤掉用户名或昵称包含'发票'的用户")
    print("- 排除无效邮箱：不再保存Guest@hydro.local等无效邮箱")

if __name__ == "__main__":
    main()