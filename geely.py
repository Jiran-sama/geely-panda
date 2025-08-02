#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import base64
import hashlib
import hmac
import uuid
import random
import requests
from datetime import datetime
from urllib.parse import quote

class GeelyUser:
    # 定义常量
    API_KEYS = {
        "204453306": "uUwSi6m9m8Nx3Grx7dQghyxMpOXJKDGu",
        "204373120": "XfH7OiOe07vorWwvGQdCqh6quYda9yGW", 
        "204167276": "5XfsfFBrUEF0fFiAUmAFFQ6lmhje3iMZ",
        "204168364": "NqYVmMgH5HXol8RB8RkOpl8iLCBakdRo",
        "204179735": "UhmsX3xStU4vrGHGYtqEXahtkYuQncMf"
    }
    
    # 基础请求头常量
    USER_AGENT = "ALIYUN-ANDROID-UA"
    APP_ID = "galaxy-app"
    APP_VERSION = "1.35.0"
    PLATFORM = "Android"
    
    def __init__(self, user_str):
        # 初始化用户信息
        self.ck_status = True
        self.token = ''
        if '&' in user_str:
            parts = user_str.split('&')
            self.refresh_token = parts[0]  # refreshToken值
            self.device_sn = parts[1]      # deviceSN值
        else:
            self.refresh_token = user_str
            self.device_sn = ''
            print("⚠️ 警告：环境变量格式不正确，应为 'refreshToken&deviceSN'")

    # 格式化UTC时间
    def format_date(self, date_obj, hour_offset=0, minute_offset=0):
        days_of_week = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # 调整时间
        timestamp = date_obj.timestamp() + hour_offset * 3600 + minute_offset * 60
        adjusted_date = datetime.fromtimestamp(timestamp)
        
        # 格式化时间字符串
        day_of_week = days_of_week[adjusted_date.weekday()]
        day = f"{adjusted_date.day:02d}"
        month = months[adjusted_date.month - 1]
        year = adjusted_date.year
        hours = f"{adjusted_date.hour:02d}"
        minutes = f"{adjusted_date.minute:02d}"
        seconds = f"{adjusted_date.second:02d}"
        
        return f"{day_of_week}, {day} {month} {year} {hours}:{minutes}:{seconds} GMT"

    # 生成UUID
    def generate_uuid(self):
        return str(uuid.uuid4())

    # 计算Content-MD5值
    def calculate_content_md5(self, request_body):
        # 将请求体转为字节数组
        byte_array = request_body.encode('utf-8')
        # 计算MD5摘要
        md5_digest = hashlib.md5(byte_array).digest()
        # 转换为Base64编码
        md5_base64 = base64.b64encode(md5_digest).decode('utf-8')
        return md5_base64

    # 计算HMAC-SHA256签名
    def calculate_hmac_sha256(self, method, accept, content_md5, content_type, date, key, nonce, timestamp, path, token=None, appcode=None):
        # 构建待加密的字符串
        string_to_sign = f"{method}\n" + \
                         f"{accept}\n" + \
                         f"{content_md5}\n" + \
                         f"{content_type}\n" + \
                         f"{date}\n"
        
        # 添加OAuth2特有的字段
        if token and appcode:
            string_to_sign += f"token:{token}\n" + \
                              f"x-ca-appcode:{appcode}\n"
                              
        string_to_sign += f"x-ca-key:{key}\n" + \
                         f"x-ca-nonce:{nonce}\n" + \
                         f"x-ca-timestamp:{timestamp}\n" + \
                         f"{path}"
        
        # 获取对应的密钥
        secret_key = self.API_KEYS.get(key, "")
        if not secret_key:
            raise ValueError(f"未知的API密钥: {key}")
        
        # 生成HMAC-SHA256签名
        h = hmac.new(secret_key.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha256)
        signature = base64.b64encode(h.digest()).decode('utf-8')
        return signature

    # 生成通用请求头
    def get_common_headers(self, key, formatted_date, nonce, timestamp, signature):
        headers = {
            'date': formatted_date,
            'x-ca-signature': signature,
            'x-ca-nonce': nonce,
            'x-ca-key': key,
            'ca_version': '1',
            'accept': 'application/json; charset=utf-8',
            'x-ca-timestamp': str(timestamp),
            'token': self.token,
            'deviceSN': self.device_sn,
            'txCookie': '',
            'appId': self.APP_ID,
            'appVersion': self.APP_VERSION,
            'platform': self.PLATFORM,
            'Cache-Control': 'no-cache',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
        }
        
        if key == "204179735":
            # 安卓端特有设置
            headers["usetoken"] = "true"
            headers["host"] = "galaxy-user-api.geely.com"
            headers["taenantid"] = "569001701001"
        else:
            # h5端特有设置
            headers["usetoken"] = "1"
            headers["host"] = "galaxy-app.geely.com"
            headers["x-refresh-token"] = "true"
            
        return headers

    # 生成GET请求头
    def get_get_header(self, key, path):
        current_date = datetime.now()
        formatted_date = self.format_date(current_date, 0)
        
        # 解析日期获取时间戳
        date_obj = datetime.strptime(formatted_date, "%a, %d %b %Y %H:%M:%S GMT")
        timestamp = int(date_obj.timestamp() * 1000)
        
        # 生成UUID和签名
        nonce = self.generate_uuid()
        signature = self.calculate_hmac_sha256(
            "GET", 
            "application/json; charset=utf-8", 
            "", 
            "application/x-www-form-urlencoded; charset=utf-8", 
            formatted_date, 
            key, 
            nonce, 
            str(timestamp), 
            path
        )
        
        # 获取通用请求头
        headers = self.get_common_headers(key, formatted_date, nonce, timestamp, signature)
        
        # GET请求特有的头部
        headers.update({
            'x-ca-signature-headers': 'x-ca-nonce,x-ca-timestamp,x-ca-key',
            'content-type': 'application/x-www-form-urlencoded; charset=utf-8',
            'user-agent': self.USER_AGENT,
        })
        
        if key == "204179735":
            headers["x-ca-appcode"] = "galaxy-app-user"
        
        return headers

    # 生成POST请求头
    def get_post_header(self, key, path, body):
        current_date = datetime.now()
        formatted_date = self.format_date(current_date, 0)
        
        # 解析日期获取时间戳
        date_obj = datetime.strptime(formatted_date, "%a, %d %b %Y %H:%M:%S GMT")
        timestamp = int(date_obj.timestamp() * 1000)
        
        # 计算Content-MD5
        content_md5 = self.calculate_content_md5(body)
        
        # 生成UUID和签名
        nonce = self.generate_uuid()
        signature = self.calculate_hmac_sha256(
            "POST", 
            "application/json; charset=utf-8", 
            content_md5, 
            "application/json; charset=utf-8", 
            formatted_date, 
            key, 
            nonce, 
            str(timestamp), 
            path
        )
        
        # 获取通用请求头
        headers = self.get_common_headers(key, formatted_date, nonce, timestamp, signature)
        
        # POST请求特有的头部
        headers.update({
            'x-ca-appcode': 'SWGeelyCode',
            'x-ca-signature-headers': 'x-ca-nonce,x-ca-timestamp,x-ca-key',
            'content-md5': content_md5,
            'user-agent': self.USER_AGENT,
            'sweet_security_info': '{"appVersion":"1.27.0","platform":"android"}',
            'methodtype': '6',
            'contenttype': 'application/json',
            'Content-Type': 'application/json; charset=utf-8',
            'Content-Length': str(len(body)),
        })
            
        return headers

    # API请求处理
    def api_request(self, method, url, headers, data=None):
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, data=data)
            else:
                raise ValueError(f"不支持的请求方法: {method}")
                
            return response.json()
        except Exception as e:
            print(f"请求出错: {e}")
            return {"code": "error", "message": str(e)}

    # 刷新Token
    def refresh_token_func(self):
        try:
            url = f"https://galaxy-user-api.geely.com/api/v1/login/refresh?refreshToken={self.refresh_token}"
            headers = self.get_get_header("204179735", f"/api/v1/login/refresh?refreshToken={self.refresh_token}")
            
            result = self.api_request("GET", url, headers)
            
            if result.get('code') == 'success':
                print(f"✅{result.get('message')}: {result['data']['centerTokenDto']['token']}")
                print(f"🆗刷新KEY: {result['data']['centerTokenDto']['refreshToken']}")
                self.ck_status = True
                self.token = result['data']['centerTokenDto']['token']
                return True
            else:
                print(f"❌ {result.get('message')}")
                self.ck_status = False
                print(result)
                return False
        except Exception as e:
            print(f"刷新Token出错: {e}")
            return False

    # 获取车机控制code接口
    def get_oauth_code(self):
        try:
            # 构建完整请求路径
            path = "/api/v1/oauth2/code"
            query = "client_id=30000025&isDestruction=false&response_type=code&scope=snsapiUserinfo"
            full_path = f"{path}?{query}"
            
            url = f"https://galaxy-user-api.geely.com{full_path}"
            headers = self.get_get_header("204179735", full_path)
            headers["x-ca-signature-headers"] = "x-ca-appcode,x-ca-nonce,x-ca-key,token,x-ca-timestamp"

            # 重新计算包含token和appcode的签名
            headers["x-ca-signature"] = self.calculate_hmac_sha256(
                "GET",
                "application/json; charset=utf-8",
                "",
                "application/x-www-form-urlencoded; charset=utf-8",
                headers["date"],
                "204179735",
                headers["x-ca-nonce"],
                headers["x-ca-timestamp"],
                full_path,
                self.token,
                "galaxy-app-user"
            )

            response = requests.get(url, headers=headers)
            
            # 检查响应状态码
            if response.status_code != 200:
                print(f"❌请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text[:200]}")
                return None
                
            # 检查响应内容是否为空
            if not response.text or response.text.isspace():
                print("❌服务器返回空响应")
                return None
                
            # 尝试解析JSON
            result = response.json()
            
            if result.get('code') == 'success':
                auth_code = result.get('data', {}).get('code')
                print(f"✅获取车机控制授权码成功: {auth_code}")
                return auth_code
            else:
                print(f"❌获取车机控制授权码失败")
                print(f"⚠️失败原因: {result}")
                return None
        except json.JSONDecodeError as e:
            print(f"❌解析JSON失败: {e}")
            print(f"服务器响应: {response.text[:500]}")
            return None
        except Exception as e:
            print(f"获取车机控制code出错: {e}")
            return None

    # 查询积分
    def check_points(self):
        try:
            url = "https://galaxy-app.geely.com/h5/v1/points/get"
            headers = self.get_get_header("204453306", "/h5/v1/points/get")
            
            result = self.api_request("GET", url, headers)
            
            if result.get('code') == "0":
                print(f"✅剩余积分: {result['data']['availablePoints']}")
                return result['data']['availablePoints']
            else:
                print("❌剩余积分查询: 失败")
                print(result)
                return 0
        except Exception as e:
            print(f"查询积分出错: {e}")
            return 0

    # 查询签到状态
    def check_sign_state(self):
        try:
            url = "https://galaxy-app.geely.com/app/v1/sign/state"
            headers = self.get_get_header("204453306", "/app/v1/sign/state")
            
            result = self.api_request("GET", url, headers)
            
            if result.get('code') == "0":
                if result.get('data') is True:
                    print("✅今日已经签到啦！")
                    return True
                else:
                    return False
            else:
                print("❌查询签到状态失败！")
                print(f"⚠️失败原因: {result}")
                return False
        except Exception as e:
            print(f"查询签到状态出错: {e}")
            return False

    # 执行签到
    def sign(self):
        try:
            # 先检查签到状态
            has_signed_today = self.check_sign_state()
            if has_signed_today:
                # 即使已经签到，也查询一下积分
                self.check_points()
                return True
            
            # 准备请求体
            body = json.dumps({"signType": 0})
            
            # 使用get_post_header生成请求头
            url = "https://galaxy-app.geely.com/app/v1/sign/add"
            headers = self.get_post_header("204453306", "/app/v1/sign/add", body)
            
            # 执行签到请求
            result = self.api_request("POST", url, headers, body)
            
            # 检查返回结果
            if result.get('code') == "0":
                print("✅签到成功！")
                # 签到成功后查询积分
                self.check_points()
                return True
            else:
                print("❌签到失败！")
                print(f"⚠️失败原因: {result}")
                return False
        except Exception as e:
            print(f"签到出错: {e}")
            return False

    # 执行签到流程
    def do_sign(self):
        print(f"⌛️ {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
        print("🔄 开始吉利银河签到")
        
        # 刷新token
        if not self.refresh_token_func():
            print("❌账号CK失效")
            return False
        
        # 执行签到
        return self.sign()


def main():
    # 获取环境变量
    user_cookie = os.environ.get("jlyh")
    
    if not user_cookie:
        print("未找到CK，请检查环境变量设置")
        return
    
    # 创建用户实例并执行签到
    user = GeelyUser(user_cookie)
    user.do_sign()
    
    # 获取车机控制授权码
    auth_code = user.get_oauth_code()


if __name__ == "__main__":
    main()
