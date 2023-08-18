import numpy as np

# 装机容量，12.16225 MW
# 发电量，1205.05 万kWh/a
X = 1205.5

# 设计年限
n = 25
# 衰减系数
r=[['1',0.02],['2-10',0.0075],['11-25',0.007]]

# 碳排放因子
cf = 0.749
# 政府补贴、综合电价、碳交易价格(
a1,a2,tr = 0.41, 0.82, 40
a3 = a1 + a2
tr = 40/1000

# 年发电量
x = [ X for i in range(n)]

rl = []
for ri in r:
    if '-' in ri[0]:
        ri1, ri2 = ri[0].split('-')
        ri1 = int(ri1)
        ri2 = int(ri2)
        for i in range(ri2-ri1+1):
            rl.append(ri[1])
    else:
        ri1 = int(ri[0])
        for i in range(1):
            rl.append(ri[1])

# check 总衰减
j = 0
for i in rl:
    j = j+i

# get 历年发电量
for i,xi in enumerate(x):
    if i == 0:
        x[i] = x[i]
    else:
        x[i] = x[i-1] * (1-rl[i-1])

# get 逐年发电量和逐年碳排放
carbon = [i * cf for i in x]
totalc = []
for i,xi in enumerate(carbon):
    if i == 0:
        totalc.append(carbon[i])
    else:
        totalc.append(carbon[i] + totalc[i-1])

# get 碳排放回收期
startc = 2181.261 # 万kgCO2
totalc_s = [ startc - i for i in totalc]
def staic_years(totalc_s, totalc):
    for i,xi in enumerate(totalc_s):
        if xi < 0:
            n_staic = i + totalc_s[i-1]/totalc[i]
            break
    return n_staic
n_carbon = staic_years(totalc_s, totalc)

