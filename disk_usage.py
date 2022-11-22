import requests
import json
import pandas as pd
import time


ip = ['172.20.118.100', '172.20.118.101', '172.20.118.102', '172.20.118.103', '172.20.118.104', '172.20.118.105']
dic1 = {
    'IP': [],
    '磁盘总大小': [],
    '已使用磁盘大小': [],
    '磁盘使用率': []
}

# 获取当前的时间戳秒为单位
t = time.time()
# 截取前面的时间戳
t = int(str(t).split('.')[0])

# 循环获取每台机器的磁盘使用率
for i in ip:
    # 获取磁盘总大小的接口地址
    url = 'https://monitor.lepass.cn/api/datasources/proxy/38/api/v1/query?' \
          'query=node_filesystem_size_bytes%7Binstance%3D~%27{0}%3A9100%27%2Cfstype%3D~%22ext3%7Cext4%7Cxfs%22%7D&time={1}'.format(i, t)
    # 把json 字符串解码为 Python 对象
    data_total = json.loads(requests.get(url).text)

    # 获取磁盘总空间
    disk_total = int(data_total['data']['result'][0]['value'][1])
    # 转换成GB
    d_total = disk_total / 1024 / 1024 / 1024
    # 保留两位小数
    d_total = '{:.2f}'.format(d_total)

    # 获取磁盘剩余空间接口地址
    url1 = 'https://monitor.lepass.cn/api/datasources/proxy/38/api/v1/query?' \
           'query=node_filesystem_avail_bytes%20%7Binstance%3D~%27{0}%3A9100%27%2Cfstype%3D~%22ext3%7Cext4%7Cxfs%22%7D&time={1}'.format(i, t)
    # 把json 字符串解码为 Python 对象
    data_free = json.loads(requests.get(url1).text)
    # 获取磁盘剩余空间
    disk_free = int(data_free['data']['result'][0]['value'][1])

    # 磁盘使用
    disk_use = disk_total - disk_free
    # 转换成GB
    d_use = disk_use / 1024 / 1024 / 1024
    # 保留两位小数
    d_use = '{:.2f}'.format(d_use)

    # 磁盘使用率
    disk_usage = disk_use / disk_total * 100
    # 保留两位小数
    disk_usage = '{:.2f}'.format(disk_usage)

    dic1.setdefault('IP', []).append(i)
    dic1.setdefault('磁盘总大小', []).append(d_total)
    dic1.setdefault('已使用磁盘大小', []).append(d_use)
    dic1.setdefault('磁盘使用率', []).append(disk_usage)

# 写入excel
df = pd.DataFrame(dic1)
df.to_excel('./2.xls', index=0)

print("Done")
