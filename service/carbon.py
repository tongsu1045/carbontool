import pandas as pd

df = pd.DataFrame()

project = "Zhangjiang Lot 58-01 Project"
df['Name'] = ['Bldg#1','Bldg#2','Bldg#3','Bldg#4','Basement']
df['Type'] = ['Office','Culture','Retail','Hotel','Parking']
df['GFA'] = [170726.47, 6886, 29372, 15950, 77613]
#df['EUI'] = [100, 200, 220, 200, 12] #综合
df['energy_intensity'] = [85.5,171,198,150,12]
df['gas_intensity'] = [1,2,3,5,0]

df['Electricity'] = df['GFA'] * df['energy_intensity']
df['Gas'] = df['GFA'] * df['gas_intensity']
df['Energy'] = df['Electricity'] + df['Gas']*10
df['EUI_s'] = df['Energy'] / df['GFA']

carbon_factor = 0.7035
gas_factor = 2.02
df['Carbon'] = carbon_factor * df['Electricity'] + gas_factor * df['Gas']
df['Scope1'] = gas_factor * df['Gas']
df['Scope2'] = carbon_factor * df['Electricity']



from pyecharts.charts import Pie

attr = df['Name'].tolist()
v1 = df['Carbon'].tolist()
pie = Pie()
pie.add(
    "",
    [list(z) for z in zip(attr, v1)],
    radius=[40, 75]
)
pie.render()



from pyecharts.charts import Sunburst

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

c = Sunburst().add("Sunburst 演示数据", data)
c.render()

bldgs = df["Name"].tolist()
data1 = []
for i,name in enumerate(bldgs):
    item = dict()
    item["name"] = name
    item["value"] = df['Carbon'][i]
    data1.append(item)
c = Sunburst().add("Sunburst 演示数据", data1)
c.render()




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