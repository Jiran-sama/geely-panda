import requests
import time
import random
import string
import hashlib
import base64
import hmac
from datetime import datetime
import json

class VehicleStatus:
    def __init__(self):
        # 基本状态信息
        self.power_mode = None  # 上电状态，"0"为上电，"1"为未上电
        
        # 位置相关
        self.altitude = None  # 海拔高度
        self.latitude = None  # 纬度
        self.longitude = None  # 经度
        self.position_can_be_trusted = None  # 位置是否可信
        
        # 车辆基础信息
        self.distance_to_empty = None  # 剩余续航里程
        self.speed = None  # 当前速度
        self.direction = None  # 方向
        self.avg_speed = None  # 平均速度
        self.fuel_type = None  # 燃料类型
        self.vin = None  # 车辆识别号
        
        # 遥控相关
        self.remote_control_inhibited = None  # 遥控器是否失效
        
        # 数据时间
        self.update_time = None  # 车辆数据上报时间
        
        # 保养信息
        self.distance_to_service = None  # 还有多少公里需要保养
        self.odometer = None  # 行驶公里数
        self.brake_fluid_level_status = None  # 制动液位状态
        self.service_warning_status = None  # 保养警告状态
        
        # 电池状态
        self.voltage = None  # 电池电压
        
        # 电动车状态
        self.is_plugged_in = None  # 是否已连接充电器
        self.aver_power_consumption = None  # 电耗
        self.pt_ready = None  # 车辆是否准备就绪，"0"未就绪，"1"就绪
        self.state_of_charge = None  # 状态充电量
        self.charge_level = None  # 电量百分比
        self.status_of_charger_connection = None  # 充电器连接状态
        self.charge_led_ctrl = None  # 充电LED控制
        self.distance_to_empty_on_battery_only = None  # 仅使用电池的续航里程
        self.is_charging = None  # 是否正在充电
        self.bmsh_chg_conn_state = None  # 充电连接状态
        self.time_to_fully_charged = None  # 充满电所需时间
        
        # 驾驶行为状态
        self.cruise_control_status = None  # 巡航控制状态
        self.engine_speed_validity = None  # 发动机转速有效性
        self.brake_pedal_depressed = None  # 刹车踏板是否被踩下
        self.transimission_gear_postion = None  # 变速器挡位位置，"3"空挡，"2"倒挡，"1"前进挡
        self.engine_speed = None  # 发动机转速
        self.brake_pedal_depressed_validity = None  # 制动踏板踩下有效性
        
        # 驾驶安全状态
        self.door_lock_status_driver_rear = None  # 后部驾驶员侧门锁状态，"0"未上锁，"1"已上锁
        self.hand_brake_status = None  # 手刹状态，"0"拉起手刹，"1"放下手刹
        self.seat_belt_status_driver = None  # 驾驶员安全带状态
        self.door_open_status_passenger = None  # 副驾驶门开启状态，"0"未打开，"1"已打开
        self.door_lock_status_passenger = None  # 副驾驶门锁状态，"0"未上锁，"1"已上锁
        self.door_open_status_driver = None  # 主驾驶门开启状态，"0"未打开，"1"已打开
        self.door_lock_status_passenger_rear = None  # 后部副驾驶侧门锁状态，"0"未上锁，"1"已上锁
        self.electric_park_brake_status = None  # 电动车制动状态，"0"驻车，"1"未驻车
        self.door_lock_status_driver = None  # 主驾驶门锁状态，"0"未上锁，"1"已上锁
        self.vehicle_alarm = None  # 车辆报警
        self.trunk_open_status = None  # 后备箱开启状态，"0"为关闭，"1"为开启

    def __str__(self):
        """返回车辆状态的字符串表示"""
        status_info = []
        
        if self.power_mode is not None:
            power_status = "上电" if self.power_mode == "0" else "未上电"
            status_info.append(f"电源状态: {power_status}")
        
        if self.vin is not None:
            status_info.append(f"车辆VIN: {self.vin}")
        
        if self.distance_to_empty is not None:
            status_info.append(f"剩余续航: {self.distance_to_empty}km")
        
        if self.odometer is not None:
            status_info.append(f"总行驶里程: {self.odometer}km")
        
        if self.distance_to_service is not None:
            status_info.append(f"保养剩余里程: {self.distance_to_service}km")
        
        if self.speed is not None:
            status_info.append(f"当前速度: {self.speed}km/h")
        
        if self.charge_level is not None:
            status_info.append(f"电量: {self.charge_level}%")
        
        if self.voltage is not None:
            status_info.append(f"电池电压: {self.voltage}V")
        
        if self.trunk_open_status is not None:
            trunk_status = "打开" if self.trunk_open_status == "1" else "关闭"
            status_info.append(f"后备箱: {trunk_status}")
        
        if self.latitude is not None and self.longitude is not None:
            status_info.append(f"位置: 经度{self.longitude}, 纬度{self.latitude}, 海拔{self.altitude}米")
            
        if self.update_time is not None:
            time_str = datetime.fromtimestamp(int(self.update_time)/1000).strftime('%Y-%m-%d %H:%M:%S')
            status_info.append(f"数据更新时间: {time_str}")
            
        return "\n".join(status_info)

class VehicleControl:
    # 定义常量
    BASE_DEVICE_URL = "https://device-api.xchanger.cn"
    BASE_AUTH_URL = "https://user-api.xchanger.cn"
    API_KEY = "67e1bd743f1c4c31841206cbb354b4af"
    
    # 请求头常量
    CONTENT_TYPE = "application/json; charset=UTF-8"
    ACCEPT = "application/json;responseformat=3"
    OPERATOR_CODE = "geelygalaxy"
    APP_ID = "galaxy_SDK"
    USER_AGENT = "okhttp/4.9.3"
    API_SIGNATURE_VERSION = "1.0"
    
    # 服务ID常量
    SERVICE_RDU = "RDU"  # 开门控制
    SERVICE_RDL = "RDL"  # 关门控制
    SERVICE_RCE = "RCE"  # 空调控制
    SERVICE_RHL = "RHL"  # 寻车
    SERVICE_RTU = "RTU"  # 后备箱控制
    
    # 命令常量
    CMD_START = "start"
    CMD_STOP = "stop"
    
    def __init__(self, vehicle_id="", authorization=None):
        # 初始化车辆控制信息
        self.vehicle_id = vehicle_id
        self.authorization = authorization
        self.power_mode = None
        self.vehicle_status = VehicleStatus()  # 创建车辆状态对象

    # 计算Content-MD5值
    def calculate_content_md5(self, request_body):
        # 将请求体转为字节数组
        byte_array = request_body.encode('utf-8')
        # 计算MD5摘要
        md5_digest = hashlib.md5(byte_array).digest()
        # 转换为Base64编码
        md5_base64 = base64.b64encode(md5_digest).decode('utf-8')
        return md5_base64

    # HMAC-SHA1签名计算
    def calculate_signature(self, nonce, body_md5_base64, timestamp, method, path, query_param=None):
        # 构建待加密的字符串
        string_to_sign = f"{self.ACCEPT}\n" + \
                        f"x-api-signature-nonce:{nonce}\n" + \
                        f"x-api-signature-version:{self.API_SIGNATURE_VERSION}\n" + \
                        f"\n" + \
                        f"{query_param or ''}\n" + \
                        f"{body_md5_base64}\n" + \
                        f"{timestamp}\n" + \
                        f"{method}\n" + \
                        f"{path}"
        
        # 生成HMAC-SHA1签名
        hmac_obj = hmac.new(self.API_KEY.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha1)
        signature = base64.b64encode(hmac_obj.digest()).decode('utf-8')
        return signature

    # 生成随机nonce
    def generate_nonce(self, timestamp):
        prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        middle = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
        return f"{prefix}-{middle}{suffix}{timestamp}"

    # 构建通用请求头
    def build_common_headers(self, nonce, signature, timestamp, host, authorization=None):
        headers = {
            "Content-Type": self.CONTENT_TYPE,
            "Accept": self.ACCEPT,
            "Connection": "Keep-Alive",
            "x-operator-code": self.OPERATOR_CODE,
            "host": host,
            "x-app-id": self.APP_ID,
            "User-Agent": self.USER_AGENT,
            "x-api-signature-version": self.API_SIGNATURE_VERSION,
            "x-api-signature-nonce": nonce,
            "x-signature": signature,
            "x-timestamp": str(timestamp)
        }
        
        if authorization:
            headers["authorization"] = authorization
            
        return headers

    # 获取授权Token
    def get_authorization(self, auth_code=""):
        # 获取当前时间戳
        timestamp = int(time.time() * 1000)
        
        # 设置API路径和参数
        path = "/auth/account/session/secure"
        query_param = "identity_type=geelygalaxy"
        url = f"{self.BASE_AUTH_URL}{path}?{query_param}"
        
        # 准备请求体
        request_body = f'{{"authCode":"{auth_code}"}}'
        
        # 计算请求体的MD5哈希并进行Base64编码
        body_md5_base64 = self.calculate_content_md5(request_body)
        
        # 生成nonce值
        nonce = self.generate_nonce(timestamp)
        
        # 计算签名
        signature = self.calculate_signature(nonce, body_md5_base64, timestamp, "POST", path, query_param)
        
        # 构造请求头
        host = self.BASE_AUTH_URL.replace("https://", "")
        headers = self.build_common_headers(nonce, signature, timestamp, host)
        
        # 发送POST请求
        try:
            self.log_operation("🔑 正在获取授权Token")
            
            response = requests.post(url, headers=headers, data=request_body)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('code') == 1000:
                    self.authorization = result['data']['accessToken']
                    print(f"✅ 授权Token获取成功")
                    return self.authorization
                else:
                    print(f"❌ 获取授权失败: {result.get('message')}")
            else:
                print(f"❌ 获取授权请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
            
            return None
        except Exception as e:
            print(f"❌ 获取授权请求异常: {str(e)}")
            return None

    # 创建远程控制请求体
    def create_control_request_body(self, command, service_id, duration=0, service_parameters=None):
        timestamp = int(time.time() * 1000)
        
        # 构建基础请求体
        request_body = {
            "command": command,
            "creator": "tc",
            "operationScheduling": {
                "duration": duration,
                "interval": 0,
                "occurs": 1,
                "recurrentOperation": False
            },
            "serviceId": service_id,
            "timestamp": timestamp
        }
        
        # 添加服务参数（如果有）
        if service_parameters:
            request_body["serviceParameters"] = service_parameters
            
        return json.dumps(request_body)

    # 发送远程控制请求
    def send_control_request(self, request_body, path=None):
        # 确保有授权Token
        if not self.authorization:
            self.get_authorization()
            if not self.authorization:
                print("❌ 无法进行操作，授权失败")
                return None
        
        # 获取当前时间戳
        timestamp = int(time.time() * 1000)
        
        # 设置API路径
        if path is None:
            path = f"/remote-control/vehicle/telematics/{self.vehicle_id}"
        
        # 完整URL
        url = f"{self.BASE_DEVICE_URL}{path}"
        
        # 计算请求体的MD5哈希并进行Base64编码
        body_md5_base64 = self.calculate_content_md5(request_body)
        
        # 生成nonce值
        nonce = self.generate_nonce(timestamp)
        
        # 计算签名
        signature = self.calculate_signature(nonce, body_md5_base64, timestamp, "PUT", path)
        
        # 构造请求头
        host = self.BASE_DEVICE_URL.replace("https://", "")
        headers = self.build_common_headers(nonce, signature, timestamp, host, self.authorization)
        
        # 发送PUT请求
        try:
            self.log_operation(f"🔄 发送请求: {path}")
            print(f"请求体: {request_body}")
            
            response = requests.put(url, headers=headers, data=request_body)
            
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            return response
        except Exception as e:
            print(f"❌ 请求发送失败: {str(e)}")
            return None
    
    # 记录操作日志
    def log_operation(self, message):
        print(f"⌛️ {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
        print(message)
    
    # 执行车辆控制操作的通用方法
    def control_vehicle(self, command, service_id, log_message, duration=0, service_parameters=None):
        self.log_operation(log_message)
        request_body = self.create_control_request_body(command, service_id, duration, service_parameters)
        return self.send_control_request(request_body)

    # 远程开门
    def open_door(self):
        return self.control_vehicle(
            command=self.CMD_START,
            service_id=self.SERVICE_RDU,
            log_message="🚪 开始执行远程开门操作"
        )

    # 远程关门
    def close_door(self):
        return self.control_vehicle(
            command=self.CMD_START,
            service_id=self.SERVICE_RDL,
            log_message="🔒 开始执行远程关门操作"
        )

    # 开启空调
    def open_air(self, temperature=20):
        return self.control_vehicle(
            command=self.CMD_START,
            service_id=self.SERVICE_RCE,
            log_message=f"❄️ 开始执行开启空调操作，温度设置为{temperature}°C",
            duration=60,
            service_parameters=[{"key": "rce", "value": str(temperature)}]
        )

    # 关闭空调
    def close_air(self):
        return self.control_vehicle(
            command=self.CMD_STOP,
            service_id=self.SERVICE_RCE,
            log_message="🔥 开始执行关闭空调操作",
            duration=60,
            service_parameters=[{"key": "rce", "value": "20"}]
        )

    # 寻车
    def search_car(self):
        return self.control_vehicle(
            command=self.CMD_START,
            service_id=self.SERVICE_RHL,
            log_message="🔍 开始执行寻车操作",
            duration=6,
            service_parameters=[{"key": "rhl", "value": "horn-light-flash"}]
        )

    # 开启后备箱
    def open_trunk(self):
        return self.control_vehicle(
            command=self.CMD_START,
            service_id=self.SERVICE_RTU,
            log_message="📦 开始执行开启后备箱操作"
        )

    # 关闭后备箱
    def close_trunk(self):
        return self.control_vehicle(
            command=self.CMD_STOP,
            service_id="RTL",
            log_message="📦 开始执行关闭后备箱操作"
        )
        
    # 获取车辆状态
    def get_vehicle_status(self, user_id=""):
        # 确保有授权Token
        if not self.authorization:
            self.get_authorization()
            if not self.authorization:
                print("❌ 无法获取车辆状态，授权失败")
                return None
        
        # 获取当前时间戳
        timestamp = int(time.time() * 1000)
        
        # 设置API路径和参数
        path = f"/remote-control/vehicle/status/state/{self.vehicle_id}"
        query_param = f"userId={user_id}"
        url = f"{self.BASE_DEVICE_URL}{path}?{query_param}"
        
        # 计算请求体的MD5哈希并进行Base64编码（GET请求没有请求体）
        body_md5_base64 = self.calculate_content_md5("")
        
        # 生成nonce值
        nonce = self.generate_nonce(timestamp)
        
        # 计算签名
        signature = self.calculate_signature(nonce, body_md5_base64, timestamp, "GET", path, query_param)
        
        # 构造请求头
        host = self.BASE_DEVICE_URL.replace("https://", "")
        headers = self.build_common_headers(nonce, signature, timestamp, host, self.authorization)
        
        # 发送GET请求
        try:
            self.log_operation("🚗 获取车辆状态信息")
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('code') == "1000":
                    # 保存powerMode字段
                    self.power_mode = result['data']['powerMode']
                    self.vehicle_status.power_mode = self.power_mode
                    power_status = "上电" if self.power_mode == "0" else "未上电"
                    print(f"✅ 获取车辆状态成功")
                    print(f"📊 车辆上电状态: {power_status} (powerMode={self.power_mode})")
                    return result['data']
                else:
                    print(f"❌ 获取车辆状态失败: {result.get('message')}")
            else:
                print(f"❌ 获取车辆状态请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
            
            return None
        except Exception as e:
            print(f"❌ 获取车辆状态请求异常: {str(e)}")
            return None
    
    # 获取详细车辆状态
    def get_vehicle_detailed_status(self, user_id=""):
        # 确保有授权Token
        if not self.authorization:
            self.get_authorization()
            if not self.authorization:
                print("❌ 无法获取车辆状态，授权失败")
                return None
        
        # 获取当前时间戳
        timestamp = int(time.time() * 1000)
        
        # 设置API路径和参数
        path = f"/remote-control/vehicle/status/{self.vehicle_id}"
        query_param = f"latest=&target=&userId={user_id}"
        url = f"{self.BASE_DEVICE_URL}{path}?{query_param}"
        
        # 计算请求体的MD5哈希并进行Base64编码（GET请求没有请求体）
        body_md5_base64 = self.calculate_content_md5("")
        
        # 生成nonce值
        nonce = self.generate_nonce(timestamp)
        
        # 计算签名
        signature = self.calculate_signature(nonce, body_md5_base64, timestamp, "GET", path, query_param)
        
        # 构造请求头
        host = self.BASE_DEVICE_URL.replace("https://", "")
        headers = self.build_common_headers(nonce, signature, timestamp, host, self.authorization)
        
        # 发送GET请求
        try:
            self.log_operation("🚗 获取详细车辆状态信息")
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('code') == "1000":
                    # 解析并保存数据到VehicleStatus对象
                    self._parse_detailed_status(result['data'])
                    
                    print(f"✅ 获取详细车辆状态成功")
                    print(self.vehicle_status)
                    
                    return result['data']
                else:
                    print(f"❌ 获取详细车辆状态失败: {result.get('message')}")
            else:
                print(f"❌ 获取详细车辆状态请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
            
            return None
        except Exception as e:
            print(f"❌ 获取详细车辆状态请求异常: {str(e)}")
            return None
    
    # 解析详细车辆状态数据
    def _parse_detailed_status(self, data):
        if not data or 'vehicleStatus' not in data:
            return
            
        vehicle_status = data['vehicleStatus']
        
        # 基础车辆状态
        if 'basicVehicleStatus' in vehicle_status:
            basic = vehicle_status['basicVehicleStatus']
            self.vehicle_status.distance_to_empty = basic.get('distanceToEmpty')
            self.vehicle_status.speed = basic.get('speed')
            self.vehicle_status.direction = basic.get('direction')
            
            # 位置信息
            if 'position' in basic:
                position = basic['position']
                self.vehicle_status.latitude = position.get('latitude')
                self.vehicle_status.longitude = position.get('longitude')
                self.vehicle_status.altitude = position.get('altitude')
                self.vehicle_status.position_can_be_trusted = position.get('posCanBeTrusted')
        
        # 配置信息
        if 'configuration' in vehicle_status:
            config = vehicle_status['configuration']
            self.vehicle_status.fuel_type = config.get('fuelType')
            self.vehicle_status.vin = config.get('vin')
        
        # 遥控器状态
        self.vehicle_status.remote_control_inhibited = vehicle_status.get('remoteControlInhibited')
        
        # 更新时间
        self.vehicle_status.update_time = vehicle_status.get('updateTime')
        
        # 附加车辆状态
        if 'additionalVehicleStatus' in vehicle_status:
            additional = vehicle_status['additionalVehicleStatus']
            
            # 保养状态
            if 'maintenanceStatus' in additional:
                maintenance = additional['maintenanceStatus']
                self.vehicle_status.distance_to_service = maintenance.get('distanceToService')
                self.vehicle_status.odometer = maintenance.get('odometer')
                self.vehicle_status.brake_fluid_level_status = maintenance.get('brakeFluidLevelStatus')
                self.vehicle_status.service_warning_status = maintenance.get('serviceWarningStatus')
                
                # 主电池状态
                if 'mainBatteryStatus' in maintenance:
                    battery = maintenance['mainBatteryStatus']
                    self.vehicle_status.voltage = battery.get('voltage')
            
            # 电动车状态
            if 'electricVehicleStatus' in additional:
                electric = additional['electricVehicleStatus']
                self.vehicle_status.is_plugged_in = electric.get('isPluggedIn')
                self.vehicle_status.aver_power_consumption = electric.get('averPowerConsumption')
                self.vehicle_status.pt_ready = electric.get('ptReady')
                self.vehicle_status.state_of_charge = electric.get('stateOfCharge')
                self.vehicle_status.charge_level = electric.get('chargeLevel')
                self.vehicle_status.status_of_charger_connection = electric.get('statusOfChargerConnection')
                self.vehicle_status.charge_led_ctrl = electric.get('chargeLEDCtrl')
                self.vehicle_status.distance_to_empty_on_battery_only = electric.get('distanceToEmptyOnBatteryOnly')
                self.vehicle_status.is_charging = electric.get('isCharging')
                self.vehicle_status.bmsh_chg_conn_state = electric.get('bmshChgConnState')
                self.vehicle_status.time_to_fully_charged = electric.get('timeToFullyCharged')
            
            # 驾驶行为状态
            if 'drivingBehaviourStatus' in additional:
                driving = additional['drivingBehaviourStatus']
                self.vehicle_status.cruise_control_status = driving.get('cruiseControlStatus')
                self.vehicle_status.engine_speed_validity = driving.get('engineSpeedValidity')
                self.vehicle_status.brake_pedal_depressed = driving.get('brakePedalDepressed')
                self.vehicle_status.transimission_gear_postion = driving.get('transimissionGearPostion')
                self.vehicle_status.engine_speed = driving.get('engineSpeed')
                self.vehicle_status.brake_pedal_depressed_validity = driving.get('brakePedalDepressedValidity')
            
            # 运行状态
            if 'runningStatus' in additional:
                running = additional['runningStatus']
                self.vehicle_status.avg_speed = running.get('avgSpeed')
            
            # 驾驶安全状态
            if 'drivingSafetyStatus' in additional:
                safety = additional['drivingSafetyStatus']
                self.vehicle_status.door_lock_status_driver_rear = safety.get('doorLockStatusDriverRear')
                self.vehicle_status.hand_brake_status = safety.get('handBrakeStatus')
                self.vehicle_status.seat_belt_status_driver = safety.get('seatBeltStatusDriver')
                self.vehicle_status.door_open_status_passenger = safety.get('doorOpenStatusPassenger')
                self.vehicle_status.door_lock_status_passenger = safety.get('doorLockStatusPassenger')
                self.vehicle_status.door_open_status_driver = safety.get('doorOpenStatusDriver')
                self.vehicle_status.door_lock_status_passenger_rear = safety.get('doorLockStatusPassengerRear')
                self.vehicle_status.electric_park_brake_status = safety.get('electricParkBrakeStatus')
                self.vehicle_status.door_lock_status_driver = safety.get('doorLockStatusDriver')
                self.vehicle_status.vehicle_alarm = safety.get('vehicleAlarm')
                self.vehicle_status.trunk_open_status = safety.get('trunkOpenStatus')

def main():
    # 创建车辆控制实例
    vehicle = VehicleControl()
    
    # 先获取授权
    vehicle.get_authorization()
    
    # 获取基本车辆状态
    vehicle.get_vehicle_status()
    
    # 获取详细车辆状态
    vehicle.get_vehicle_detailed_status()
    
    # 执行开门操作
    # vehicle.close_trunk()


if __name__ == "__main__":
    main()
