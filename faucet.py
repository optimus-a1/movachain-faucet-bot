import requests
import json
import csv
import time
from datetime import datetime
import os

# 代理配置
PROXY = "geo.iproyal.com:12321"
PROXY_AUTH = "eL2jPkQ4Oo5O7jeQ:F4OKzobo18XQwFEC"

class FinalMarsFaucet:
    def __init__(self):
        self.base_url = "https://faucet.mars.movachain.com"
        self.api_endpoint = "/api/faucet/v1/transfer"
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "content-type": "application/json",
            "origin": "https://faucet.mars.movachain.com",
            "referer": "https://faucet.mars.movachain.com/",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        }
    
    def create_session_with_proxy(self):
        """创建带代理的新会话"""
        session = requests.Session()
        session.headers.update(self.headers)
        session.proxies.update({
            'http': f'http://{PROXY_AUTH}@{PROXY}',
            'https': f'http://{PROXY_AUTH}@{PROXY}'
        })
        return session
    
    def get_current_ip(self, session):
        """获取当前IP地址"""
        try:
            response = session.get('https://api.ipify.org?format=json', timeout=10)
            if response.status_code == 200:
                return response.json().get('ip', 'unknown')
        except:
            pass
        return 'unknown'
    
    def request_faucet_with_page_visit(self, address):
        """使用方法1：先访问主页获取会话，再请求水龙头"""
        # 每次请求都创建新的代理会话
        session = self.create_session_with_proxy()
        
        try:
            # 获取当前IP
            current_ip = self.get_current_ip(session)
            print(f"当前使用IP: {current_ip}")
            
            # 步骤1: 先访问主页，获取会话状态
            print("正在访问主页获取会话...")
            main_response = session.get(self.base_url + "/", timeout=10)
            
            if main_response.status_code != 200:
                return {
                    "success": False,
                    "tx_hash": "",
                    "error_msg": f"主页访问失败: {main_response.status_code}",
                    "error_code": str(main_response.status_code),
                    "ip": current_ip
                }
            
            # 步骤2: 执行水龙头转账请求
            print("正在请求水龙头转账...")
            url = self.base_url + self.api_endpoint
            payload = {"to": address}
            
            response = session.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    tx_hash = data.get("data", "")
                    if isinstance(tx_hash, bool):
                        tx_hash = str(tx_hash)
                    
                    # 判断是否成功
                    is_success = (data.get("error") == "200" and 
                                 tx_hash and tx_hash != "false" and tx_hash != "False")
                    
                    return {
                        "success": is_success,
                        "tx_hash": tx_hash,
                        "error_msg": data.get("err_msg", ""),
                        "error_code": data.get("error", ""),
                        "response_data": data,
                        "ip": current_ip
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "tx_hash": "",
                        "error_msg": "响应不是有效JSON",
                        "error_code": "JSON_ERROR",
                        "response_data": response.text,
                        "ip": current_ip
                    }
            else:
                return {
                    "success": False,
                    "tx_hash": "",
                    "error_msg": f"HTTP {response.status_code}",
                    "error_code": str(response.status_code),
                    "response_data": response.text,
                    "ip": current_ip
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "tx_hash": "",
                "error_msg": "请求超时",
                "error_code": "TIMEOUT",
                "response_data": "",
                "ip": current_ip
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "tx_hash": "",
                "error_msg": str(e),
                "error_code": "REQUEST_ERROR",
                "response_data": "",
                "ip": current_ip
            }
        finally:
            # 关闭会话
            session.close()
    
    def save_results(self, results, filename="final_results.csv"):
        """保存结果到CSV文件"""
        fieldnames = ["时间", "地址", "状态", "交易哈希", "错误信息", "错误代码", "使用IP"]
        
        # 检查文件是否存在
        file_exists = os.path.exists(filename)
        
        with open(filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            for result in results:
                # 确保所有必需的字段都存在
                safe_result = {}
                for field in fieldnames:
                    safe_result[field] = result.get(field, "")
                writer.writerow(safe_result)
    
    def read_addresses(self, filename="add.txt"):
        """从文件中读取地址列表"""
        addresses = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    address = line.strip()
                    if address and address.startswith('0x'):
                        addresses.append(address)
            print(f"成功读取 {len(addresses)} 个地址")
            return addresses
        except FileNotFoundError:
            print(f"错误: 找不到文件 {filename}")
            return []
        except Exception as e:
            print(f"读取地址文件时出错: {e}")
            return []
    
    def run(self, delay=3):
        """运行主程序"""
        print("=== Mars Movachain 水龙头领水程序（方法1：访问主页获取会话）===\n")
        
        # 读取地址
        addresses = self.read_addresses()
        if not addresses:
            print("没有找到有效的地址，程序退出")
            return
        
        print(f"准备为 {len(addresses)} 个地址请求测试币")
        print(f"使用方法: 访问主页获取会话")
        print(f"请求间隔: {delay} 秒\n")
        
        results = []
        success_count = 0
        
        for i, address in enumerate(addresses, 1):
            print(f"[{i}/{len(addresses)}] 正在处理地址: {address}")
            print("正在获取新IP...")
            
            # 发送请求
            result = self.request_faucet_with_page_visit(address)
            
            # 准备CSV记录
            csv_record = {
                "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "地址": address,
                "状态": "成功" if result["success"] else "失败",
                "交易哈希": result["tx_hash"],
                "错误信息": result["error_msg"],
                "错误代码": result["error_code"],
                "使用IP": result.get("ip", "unknown")
            }
            
            results.append(csv_record)
            
            # 打印结果
            if result["success"]:
                success_count += 1
                print(f"✅ 成功! 交易哈希: {result['tx_hash']}")
            else:
                print(f"❌ 失败! 错误: {result['error_msg']}")
            
            # 保存当前结果（实时保存）
            self.save_results([csv_record])
            
            # 如果不是最后一个地址，则等待
            if i < len(addresses):
                print(f"等待 {delay} 秒后处理下一个地址...\n")
                time.sleep(delay)
        
        # 输出统计信息
        print("\n" + "=" * 60)
        print("=== 执行完成 ===")
        print(f"总处理地址数: {len(addresses)}")
        print(f"成功数: {success_count}")
        print(f"失败数: {len(addresses) - success_count}")
        print(f"成功率: {(success_count/len(addresses)*100):.1f}%")
        print(f"结果已保存到: final_results.csv")
        
        # 显示成功的交易
        if success_count > 0:
            print(f"\n🎉 成功的交易:")
            for result in results:
                if result["状态"] == "成功":
                    print(f"  地址: {result['地址']}")
                    print(f"  交易哈希: {result['交易哈希']}")
                    print(f"  时间: {result['时间']}")
                    print(f"  IP: {result['使用IP']}")
                    print("-" * 40)

def main():
    """主函数"""
    faucet = FinalMarsFaucet()
    
    # 可以修改请求间隔（秒）
    delay = 3
    
    try:
        faucet.run(delay=delay)
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n程序执行出错: {e}")

if __name__ == "__main__":
    main()
