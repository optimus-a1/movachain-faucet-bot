---

````markdown
# MovaChain Faucet Bot

一个自动化的 **MovaChain Faucet 机器人**，用于批量请求测试币。  
支持从地址文件读取钱包地址，并支持代理池功能（已集成 [IPRoyal 代理服务](https://iproyal.cn/?r=910103)）。

---

## 文件说明

- `faucet.py`  
  主程序文件，包含自动请求 Faucet 的逻辑。  

- `add.txt`  
  钱包地址列表文件，每行一个地址。  

---

## 安装与环境配置

### 1. 克隆项目
```bash
git clone https://github.com/optimus-a1/movachain-faucet-bot.git
cd movachain-faucet-bot
````

### 2. 创建虚拟环境（可选，但推荐）

```bash
python3 -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

### 3. 安装依赖

项目基于 Python3，依赖主要包括：

* `requests`  用于 HTTP 请求
* `fake-useragent`  随机生成 User-Agent
* `colorama`  终端彩色输出

安装依赖：

```bash
pip install requests fake-useragent colorama
```

---

## 配置代理

在 **faucet.py** 中找到以下配置并修改为你的代理账号：

```python
# 代理配置
PROXY = "geo.iproyal.com:12321"
PROXY_AUTH = "你的代理用户名:密码"   # 这里需要改成你自己的
```

> 推荐使用 [IPRoyal 代理](https://iproyal.cn/?r=910103)，稳定性较好。
> 如果没有代理，也可以先注释掉相关逻辑，直接运行。

---

## 使用方法

1. 编辑 `add.txt` 文件，把需要请求 Faucet 的钱包地址填进去，每行一个，例如：

   ```
   0x1234567890abcdef1234567890abcdef12345678
   0xabcdefabcdefabcdefabcdefabcdefabcdefabcd
   ```

2. 运行脚本：

   ```bash
   python faucet.py
   ```

3. 程序会依次读取 `add.txt` 中的地址，并通过代理请求 Faucet。

---

## 注意事项

* 本项目仅供学习和测试使用。
* 请合理使用，不要对 Faucet 服务器造成过大压力。
* 如果遇到 IP 限制6小时领取一次，建议使用代理池。
* 推荐代理：[IPRoyal 注册链接](https://iproyal.cn/?r=910103)

---


```
