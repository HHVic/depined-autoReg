# depined-autoReg
depined批量注册 含推荐码激活

## 1. install
```shell
pip install -r requirements.txt
```

## 2. config your account

### 2.1 accounts.csv 提供推荐码的账号
```text
email,proxy,token
...
```
### 2.2 proxies.csv 注册用户时使用的代理（随机选取）
```text
proxy
...
```
### 2.3 register.csv 需要注册的用户
```text
email,password
...
```

## 3. run
```shell
python register.py
```
