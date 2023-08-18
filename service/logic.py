import pandas as pd
import numpy as np
from pyecharts.charts import Sunburst
from pyecharts import options as opts

# 获取碳排放因子
cfdb = pd.read_csv("../static/carbonfactor.csv")

#cftype, city = "全国电网", "上海"
#cftype, city = "区域电网", "上海"
cftype, city = "省级电网", "上海" #从前端获取

if cftype == "全国电网":
  cfactor = float(cfdb[cfdb['简称'] == cftype]['碳排放因子'])
else:
  cfactor = float(cfdb[(cfdb['简称']==cftype) & (cfdb['省份']==city)]['碳排放因子'])
gfactor = 2.02

# --------------------获取建筑信息，计算能耗-----------------------------------
# input df (building information), return eui columns
# input area, return carbon
# 下方df从前端获取
df = pd.DataFrame([['1#办公',"商业办公(集中空调系统)",50000],
                   ['2#宾馆',"宾馆(五星级)",10000],
                   ['3#宾馆',"宾馆(五星级)",20000]],
                  columns = ['名称','建筑类型','面积'])
# 扩充能耗强度默认值
euidb = pd.read_csv("../static/energyuseintensity.csv")
df = df.merge(euidb,how='left') #key step
# 上一步直接用前端解决吧，js读取csv，前端匹配类型，前端返回一个不用修改的df
#return df to front-end, and get a user  revised one for further calc
# 从前端获取一个用户修改过的df做接下来的计算
df['综合能耗'] = df['面积'] * df['综合默认值'] #kWh
df['用电能耗'] = df['面积'] * df['用电默认值'] #kWh
df['用气量'] = df['面积'] * df['燃气默认值'] #m3

df['综合碳排放'] = df['面积'] * df['综合默认值'] * cfactor * 0.001 #tCO2
df['用电碳排放'] = df['面积'] * df['用电默认值'] * cfactor * 0.001 #tCO2
df['用气碳排放'] = df['面积'] * df['燃气默认值'] * gfactor * 0.001 #tCO2

# plotting
# general carbon plot, building vs carbon
df1 = df[['名称','综合碳排放']]
carbon_total = df['综合碳排放'].sum()
carbon_intensity = carbon_total / df['面积'].sum() * 1000
# carbon by scope, scope vs
df2 = df[['名称','用电碳排放','用气碳排放']]
df2 = df2.set_index('名称')
df2 = df2.stack().reset_index()
df2.columns = ['名称','用能类型','碳排放']

def to_scope(x):
  if x == '用电碳排放': return "范围二"
  else: return "范围一"

df2['范围'] = df2['用能类型'].apply(lambda x: to_scope(x))
# need to write a function transform df to pyechart sunburst data structure
# target: data = [{"name": level-1, "children": [name, value, children]}, {...}]
# df2[['范围','名称','碳排放']].to_dict()
def to_sunburst(df):
  data = []
  level1 = df['范围'].drop_duplicates().reset_index(drop=True)
  level2 = df['名称'].drop_duplicates().reset_index(drop=True)
  for i in range(len(level1)):
    child = []
    for j in range(len(level2)):
      value = float(df[(df['名称']==level2[j]) & (df['范围']==level1[i])]['碳排放'])
      child.append({"name": level2[j],"value":value})
    data.append({"name": level1[i],"children":child})
  return data

# -------------------对标-------------------------------------------------
# 从前端获取filter，城市、新建/既有、建筑功能、建筑特征（超高层/综合体）、面积范围、年份范围
# 筛选数据库
filters = {
  "对标城市": ['上海'],
  "既有与否": [],
  "建筑特征": ['综合体'],
  "建筑功能": [],
  "面积范围": [],
  "年份": []
}

bc = pd.read_csv("../static/buildingcarbon.csv")
bc['年份'].fillna(pd.Timestamp.today().year) # 所有新建的，默认是最新年份

# 这个filter部分待完善
bcf = bc[(bc['城市'].isin(filters['对标城市'])) & (bc['特征'].isin(filters['建筑特征']))]
bcf = bcf[['项目', '碳排放', '单位面积碳排放']]
bcf.columns = ['project', 'carbon', 'cui'] #换成英文好转换为dict/json让前端引用

# 从后台获取本项目 名称、碳排放量、CUI
# 和数据库的数据concat
bcf.loc[0] =["本项目",carbon_total,carbon_intensity]
# 或者用下句插入行
# pd.DataFrame(np.insert(df.values, 4, values=[1, 7, 6], axis=0))
# 传递去前端画图
#bcfd = bcf.to_dict('records')
bcfd = bcf.to_dict('list')

# 对标图2
# df提取之前，先按 建筑类型 group一遍，确保对标的类型一致
df3 = df.groupby(['建筑类型'])[['综合碳排放','面积']].sum().reset_index()
df3['单位面积碳排放'] = df3['综合碳排放'] / df3['面积'] *1000
df3 = df3.merge(euidb,how='left')
df3 = df3[['建筑类型','引导值','约束值','单位面积碳排放']]
df3.columns = ['buildingtype', 'high', 'low', 'carbonintensity']
df3['between'] = df3['high'] - df3['low']
df3d = df3.to_dict('list')
# df3d = df3[['buildingtype', 'carbonintensity']].to_dict('list')
# df3d['value'] = df3[['low', 'high']*2].to_numpy()


# ------------------节能措施------------------------------------------------
# 用户选择节能措施 和 节能比例
strategy, rate = ['自然通风','利用天然采光','冷辐射吊顶'], [0.08,0.04,0.04] # 用户输入

def getfilter(strategy):
  if strategy == '自然通风':
    buildingtypes = ['商业办公(半集中、分散式空调系统)','宾馆(五星级)','宾馆(四星级)','宾馆(三星级)','购物中心','百货','餐饮店','一般商铺']
  elif strategy in ['利用天然采光','冷辐射吊顶']:
    buildingtypes = ['国家机关办公', '商业办公(集中空调系统)', '商业办公(半集中、分散式空调系统)', '宾馆(五星级)', '宾馆(四星级)',
                   '宾馆(三星级)', '购物中心', '百货', '超市及仓储', '餐饮店', '一般商铺', '教育', '文化展厅', '图书馆',
                   '标准化实验室', '体育建筑', '宿舍', '医疗卫生', '其他']
  else:
    pass
  return buildingtypes

df4 = df[['名称', '建筑类型', '面积', '用电碳排放', '用气碳排放', '综合碳排放']]
for i,eachstr in enumerate(strategy):
  print(rate[i],eachstr)
  buildingtypes = getfilter(eachstr)
  df4['rate'] = df4['建筑类型'].apply(lambda x: rate[i] if x in buildingtypes else 0)
  df4.insert(df4.shape[1],eachstr,(1-df4['rate'])*df4['综合碳排放'])


# plot sankey
# data structure
# data = [{name: 'A'},{name: 'B'}], link = [{source: 'A',target: 'B',value: 5}, {}]





c = (
    Sunburst(init_opts=opts.InitOpts(width="1000px", height="600px"))
    .add(
        "",
        data_pair=data,
        highlight_policy="ancestor",
        radius=[0, "95%"],
        sort_="null",
        levels=[
            {},
            {
                "r0": "15%",
                "r": "35%",
                "itemStyle": {"borderWidth": 2},
                "label": {"rotate": "tangential"},
            },
            {"r0": "35%", "r": "70%", "label": {"align": "right"}},
            {
                "r0": "70%",
                "r": "72%",
                "label": {"position": "outside", "padding": 3, "silent": False},
                "itemStyle": {"borderWidth": 3},
            },
        ],
    )
    .set_global_opts(title_opts=opts.TitleOpts(title="Sunburst-官方示例"))
    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}"))
    .render("drink_flavors.html")
)
