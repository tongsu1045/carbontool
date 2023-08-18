import pandas as pd
# 基础能耗计算
df = pd.DataFrame()

project = "Zhangjiang Lot 58-01 Project"
df['Name'] = ['Bldg#1','Bldg#2','Bldg#3','Bldg#4','Basement']
df['Type'] = ['办公楼','文化','商业','酒店(五星级)','停车']
df['GFA'] = [170726.47, 6886, 29372, 15950, 77613]
df['tEUI'] = [100, 200, 220, 200, 12] #综合,kWh/m2/a
df['heatsource'] = ['g','e','g','g',None]
def heatui(df):
    if (df.heatsource == 'g') & (df.Type =='Hotel'):
        df.eui = df.tEUI * 0.7
    elif df.heatsource == 'g':
        df.eui = df.tEUI * 0.9
    else:
        df.eui = df.tEUI
    return df.eui
#df['EUI'] = [85.5,171,198,150,12] #energy_intensity,kWh/m2/a
#df['GUI'] = [1,2,3,5,0] #gas_intensity,m3/m2/a
df['EUI'] = df.apply(heatui,axis=1)
df['GUI'] = (df['tEUI'] - df['EUI'])/10 #m3/m2/a

df['Electricity'] = df['GFA'] * df['EUI'] #kWh
df['Gas'] = df['GFA'] * df['GUI'] #m3
df['Energy'] = df['Electricity'] + df['Gas']*10 #kWh

# 复选框
province = "上海"
city = "上海"
cfcode = "1"
# 1- 《2011 年和 2012 年中国区域电网平均 CO2 排放因子》
# 2- 《生态环境部关于商请提供2018年度省级人民政府控制温室气体排放目标责任落实情况自评估报告的函》
# 3- 生态环境部全国电网平均排放因子
def find_cf(city, cfcode):
    pass

carbon_factor = 0.7035
gas_factor = 2.02
df['Scope1'] = gas_factor * df['Gas'] / 1000 #tCO2
df['Scope2'] = carbon_factor * df['Electricity'] / 1000 #tCO2
df['Carbon'] = df['Scope1'] + df['Scope2']

#data = df[['Name','Scope1','Scope2']].set_index('Name').stack()

scopes = [i for i in df.columns if 'Scope' in i]
data = []
for i in scopes:
    item = dict()
    item["name"] = i
    item["children"] = []
    for j,value in enumerate(df[i].tolist()):
        x = {"name": df['Name'][j], "value": value}
        item["children"].append(x)
    data.append(item)


from pyecharts.charts import Sunburst
from pyecharts import options as opts

c = Sunburst(init_opts=opts.InitOpts(width="1000px", height="600px"))
c.add(
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
c.set_global_opts(title_opts=opts.TitleOpts(title="碳排放组成"))
c.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}"))
c.render("render.html")


# 对标部分
# 图1 - 和55015对标
df1 = df[['Type','GFA','Scope1','Scope2','Carbon']].groupby(['Type']).sum()
df1['CUI'] = df1['Carbon'] / df1['GFA'] * 1000

od = pd.DataFrame([[80,110],[210,260],[180,240],[150,200],[120,160]],
                  index=['办公楼','商业','酒店(五星级)','酒店(四星级)','酒店(三星级)'],
                  columns=['引导值','约束值'])
df2 = df1.merge(od,left_on=df1.index,right_on=od.index)
df2['差值'] = df2['约束值']- df2['引导值']


import pyecharts.options as opts
from pyecharts.charts import Bar, Line, Scatter
bar = Bar()
bar.add_xaxis(xaxis_data=df2.iloc[:,0].tolist())
bar.add_yaxis(
    series_name="引导值",
    y_axis=df2['引导值'].tolist(),
    label_opts=opts.LabelOpts(is_show=False),
    stack="stack1"
)
bar.add_yaxis(
    series_name="约束值",
    y_axis=df2['差值'].tolist(),
    label_opts=opts.LabelOpts(is_show=False),
    stack="stack1"
)
sc = Scatter()
sc.add_xaxis(xaxis_data=df2.iloc[:,0].tolist())
sc.add_yaxis(
    series_name="本项目",
    y_axis=df2['CUI'].tolist(),
    symbol_size=20,
    color="#d14a61",
)
sc.yaxis_opts=opts.AxisOpts(name="碳排放强度（kgCO2/m2/a）")
sc.overlap(bar).render("render.html")

from pyecharts.charts import Gauge

c = (
    Gauge()
    .add(
        series_name = "碳排放",
        data_pair = [(df2.iloc[:,0].tolist()[0], df2['CUI'][0])],
        max_=150,
        axisline_opts=opts.AxisLineOpts(
            linestyle_opts=opts.LineStyleOpts(
                color=[(df2['引导值'][0]/150, "#67e0e3"), (df2['约束值'][0]/150, "#37a2da"), (1, "#fd666d")], width=30
            )
        ),
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="碳排放对标"),
        legend_opts=opts.LegendOpts(is_show=False),
        tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{a} <br/>{b} : {c} kgCO2/m2/a"),
    )
    .render("render.html")
)

# 图2 - 和既有项目数据库对标
pod = pd.read_excel(r"C:\Users\tong.su\Downloads\existingcarbon.xlsx")
x_data = df2.iloc[:,0].tolist()
y_data = []
for item in x_data:
    y_data.append(pod[pod['Usage Type']==item]['Carbon Intensity(kgCO2/m2·a)'].tolist())

scatter_data = df2['CUI'].tolist()

import pyecharts.options as opts
from pyecharts.charts import Grid, Boxplot, Scatter

box_plot = Boxplot()
box_plot = (
    box_plot.add_xaxis(xaxis_data=x_data)
    .add_yaxis(series_name="", y_axis=box_plot.prepare_data(y_data))
    .set_global_opts(
        title_opts=opts.TitleOpts(
            pos_left="center", title="碳排放对标"
        ),
        tooltip_opts=opts.TooltipOpts(trigger="item", axis_pointer_type="shadow"),
        xaxis_opts=opts.AxisOpts(
            type_="category",
            boundary_gap=True,
            splitarea_opts=opts.SplitAreaOpts(is_show=False),
            #axislabel_opts=opts.LabelOpts(formatter="expr {value}"),
            splitline_opts=opts.SplitLineOpts(is_show=False),
        ),
        yaxis_opts=opts.AxisOpts(
            type_="value",
            name="kgCO2/m2/a",
            splitarea_opts=opts.SplitAreaOpts(
                is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
            ),
        ),
    )
    .set_series_opts(tooltip_opts=opts.TooltipOpts(formatter="{b}: {c}"))
)

scatter = (
    Scatter()
    .add_xaxis(xaxis_data=x_data)
    .add_yaxis(series_name="", y_axis=scatter_data)
    .set_global_opts(
        title_opts=opts.TitleOpts(
            pos_left="10%",
            pos_top="90%",
            #title="upper: Q3 + 1.5 * IQR \nlower: Q1 - 1.5 * IQR",
            title_textstyle_opts=opts.TextStyleOpts(
                border_color="#999", border_width=1, font_size=14
            ),
        ),
        yaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(is_show=False),
            axistick_opts=opts.AxisTickOpts(is_show=False),
        ),
    )
)

grid = (
    Grid()
    .add(
        box_plot,
        grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", pos_bottom="15%"),
    )
    .add(
        scatter,
        grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", pos_bottom="15%"),
    )
    .render("render.html")
)

# 能耗分项
bg = pd.DataFrame([[0.227967041,0.181130986,0.076555078,0.260107859,0.006730839,0.049531956,0.141389466,0.016586774,0.04,],
                   [0.249335323,0.257945981,0.094626424,0.13802145,0.016143543,0.02778717,0.080711101,0.04779858,0.04,0.047631086],
                   [0.231313536,0.122887953,0.162875563,0.145492346,0.002249377,0.010922428,0.134467925,0.055019792,0.04,0.094751143],
                   [0.231313536,0.122887953,0.162875563,0.145492346,0.002249377,0.010922428,0.134467925,0.055019792,0.04,0.094751143],
                   [0.231313536,0.122887953,0.162875563,0.145492346,0.002249377,0.010922428,0.134467925,0.055019792,0.04,0.094751143]],
                  index=['办公楼','商业','酒店(五星级)','酒店(四星级)','酒店(三星级)'],
                  columns=['照明','设备','制热','供冷','冷却塔','水泵','风机','室外照明','电梯','生活用水'])




# PV calculation
PVarea = 1205.5*10000/120 #1205.5万kWh
PVele = 1205.5*10000 #kWh
CF = 0.749
N = 25
butie = 0.42 # 补贴
dianfei = 0.81 # 平均电费
#trading = 40.05 #元/ton
trading = 567.57
invest = 11500*10000 #建设期投资，元
Carbon_build = 21812614.07 #建设期碳排放，kg
shuaijian = [['1',0.02],['2-10',0.0075],['11-25',0.007]]
r = []
for i in shuaijian:
    if '-' in i[0]:
        m = int(i[0].split('-')[0])
        n = int(i[0].split('-')[1])
        for j in range(n-m+1):
            r.append(i[1])
    else:
        r.append(i[1])
r.insert(0,0)
r.pop()
pvdf = pd.DataFrame()
pvdf['逐年衰减比例'] = r
#pvdf['power'] = PVele * (1-pvdf['年衰减比例']) # 用哪种算法？
pvdf['逐年衰减电量'] = PVele * pvdf['逐年衰减比例']
pvdf['累计衰减电量'] = pvdf['逐年衰减电量'].cumsum()
pvdf['逐年发电量'] = PVele - pvdf['累计衰减电量']
pvdf['逐年减排量'] = CF * pvdf['逐年发电量']
pvdf['累计发电量'] = pvdf['逐年发电量'].cumsum()
pvdf['累计减排量'] = pvdf['逐年减排量'].cumsum()
pvdf['累计碳排放量'] = Carbon_build - pvdf['累计减排量']

def roi(flow, cum):
    for i,item in enumerate(cum):
        a = None
        if item < 0:
            a = i + cum[i-1] / flow[i]
            break
    return a

roi_carbon = roi(flow=pvdf['逐年减排量'].tolist(),cum=pvdf['累计碳排放量'].tolist())

pvdf['逐年补贴'] = butie * pvdf['逐年发电量']
pvdf['逐年节约'] = dianfei * pvdf['逐年发电量']
pvdf['逐年收益'] = pvdf['逐年补贴'] + pvdf['逐年节约']
pvdf['累计补贴'] = invest - butie * pvdf['累计发电量']
pvdf['累计节约'] = invest - dianfei * pvdf['累计发电量']
pvdf['累计收益'] = invest - (butie+dianfei) * pvdf['累计发电量']

roi_i1 = roi(pvdf['逐年收益'].tolist(),pvdf['累计收益'].tolist())
roi_i2 = roi(pvdf['逐年补贴'].tolist(),pvdf['累计补贴'].tolist())
roi_i3 = roi(pvdf['逐年节约'].tolist(),pvdf['累计节约'].tolist())

pvdf['碳交易收益'] = trading/1000 * pvdf['逐年减排量']
pvdf['逐年节约考虑碳交易'] = pvdf['逐年节约'] + pvdf['碳交易收益']
pvdf['累计收益考虑碳交易'] = invest - trading/1000 * pvdf['累计减排量'] - dianfei * pvdf['累计发电量']

roi_t1 = roi(pvdf['逐年节约考虑碳交易'].tolist(),pvdf['累计收益考虑碳交易'].tolist())


from pyecharts.charts import Line
from pyecharts import options as opts
from pyecharts.globals import ThemeType

xaxis = [i+1 for i in range(N)]
yaxis1 = pvdf['逐年减排量'].cumsum().tolist()
yaxis2 = [Carbon_build for i in range(N)]
line = Line()
line.add_xaxis(xaxis)
line.add_yaxis("累计减排量", yaxis1,is_symbol_show=False)
line.add_yaxis("全生命周期碳排放量", yaxis2,is_symbol_show=False)
line.render()

#xaxis = [i+1 for i in range(N)]
yaxis_avg = [invest for i in range(N)]
yaxis21 = pvdf['逐年补贴'].cumsum().tolist()
yaxis22 = pvdf['逐年节约'].cumsum().tolist()
yaxis23 = pvdf['逐年收益'].cumsum().tolist()
line2 = Line()
line2.add_xaxis(xaxis)
line2.add_yaxis("项目总投资", yaxis_avg,is_symbol_show=False)
line2.add_yaxis("累计补贴", yaxis21,is_symbol_show=False)
line2.add_yaxis("累计节省电价", yaxis22,is_symbol_show=False)
line2.add_yaxis("综合累计优惠", yaxis23,is_symbol_show=False)
line2.render()


#xaxis = [i+1 for i in range(N)]
#yaxis_avg = [invest for i in range(N)]
yaxis31 = pvdf['碳交易收益'].cumsum().tolist()
yaxis32 = pvdf['逐年节约考虑碳交易'].cumsum().tolist()
line3 = Line()
line3.add_xaxis(xaxis)
line3.add_yaxis("项目总投资", yaxis_avg,is_symbol_show=False)
line3.add_yaxis("碳交易额", yaxis31,is_symbol_show=False)
line3.add_yaxis("综合累计优惠", yaxis32,is_symbol_show=False)
line3.render()