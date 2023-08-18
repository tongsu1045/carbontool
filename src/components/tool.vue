<template>
  <div class="content">
    <Form ref="formDynamic" :model="formDynamic" :label-width="80" style="width: 600px">
        <FormItem label="选择城市">
            <Select v-model="model1" style="width:200px">
                <Option v-for="item in cityList" :value="item.value" :key="item.value">{{ item.label }}</Option>
            </Select>
        </FormItem>
        <FormItem label="电力碳排放因子来源">
            <Select v-model="model1" style="width:200px">
                <Option v-for="item in CFsource" :value="item.value" :key="item.value">{{ item.label }}</Option>
            </Select>
        </FormItem>
        <FormItem
                v-for="(item, index) in formDynamic.items"
                v-if="item.status"
                :key="index"
                :label="'区域 ' + item.index"
                :prop="'items.' + index + '.value'"
                :rules="{required: true, message: 'Item ' + item.index +' can not be empty', trigger: 'blur'}">
            <Row>
                <Col span="10">
                    <Select v-model="item.value" style="width: 200px">
                        <Option v-for="ele in typeList" :value="ele.value" :key="ele.value">{{ ele.label }}</Option>
                    </Select>
                </Col>
                <Col span="10">
                    <Input type="text" v-model="item.value2" placeholder="输入面积" style="width: 200px"></Input>
                </Col>
                <Col span="4">
                    <Button @click="handleRemove(index)">Delete</Button>
                </Col>
            </Row>
        </FormItem>
        <FormItem>
            <Row>
                <Col span="12">
                    <Button type="dashed" long @click="handleAdd" icon="md-add">Add item</Button>
                </Col>
            </Row>
        </FormItem>
        <FormItem>
            <Button type="primary" @click="handleSubmit('formDynamic')">Submit</Button>
            <Button @click="handleReset('formDynamic')" style="margin-left: 8px">Reset</Button>
        </FormItem>
    </Form>
    <Content :style="{padding: '24px'}">
        <div id='echart1' style="width: 940px;height: 500px;"></div>
        <div id='echart2' style="width: 940px;height: 500px;"></div>
        <div id='echart3' style="width: 940px;height: 500px;"></div>
    </Content>
  </div>
</template>

<script>
    import echarts from 'echarts';
    export default {
        data () {
            return {
                index: 1,
                showEcharts1: true,
                showEcharts2: true,
                formDynamic: {
                    items: [
                        {

                            value: '',
                            value2: '',
                            index: 1,
                            status: 1
                        }
                    ]
                },
                CFsource: [
                    {
                        value: '1',
                        label: '《2011 年和 2012 年中国区域电网平均 CO2 排放因子》'
                    },
                    {
                        value: '2',
                        label: '《生态环境部关于商请提供2018年度省级人民政府控制温室气体排放目标责任落实情况自评估报告的函》'
                    },
                    {
                        value: '3',
                        label: '2022全国电网平均排放因子'
                    }],
                cityList: [],
                typeList: [
                    {
                        value: 'office',
                        label: '办公'
                    },
                    {
                        value: 'mixeduse',
                        label: '综合楼'
                    },
                    {
                        value: 'retail',
                        label: '商业'
                    },
                    {
                        value: 'residence',
                        label: '宿舍'
                    }
                ]
            }
        },
        created(){
            this.$axios
                .get('/cities')
                .then(response => (this.cityList = response.data.province))
                .catch(function (error) { // 请求失败处理
                console.log(error);
                });
        },
        methods: {
            handleSubmit (name) {
                this.$refs[name].validate((valid) => {
                    if (valid) {
                        this.$Message.success('Success!');
                        this.$axios.post('/api',formDynamic)
                            .then((res) => {console.log('数据',res);});
                    } else {
                        this.$Message.error('Fail!');
                    }
                })
            },
            handleReset (name) {
                this.$refs[name].resetFields();
            },
            handleAdd () {
                this.index++;
                this.formDynamic.items.push({
                    value: '',
                    index: this.index,
                    status: 1
                });
            },
            handleRemove (index) {
                this.formDynamic.items[index].status = 0;
            }
        },
        mounted() {
            let self = this;
            let myChart = this.$echarts.init(document.getElementById('echart1'))
            // 基于准备好的dom，初始化echarts实例
            //var myChart = echarts.init(document.getElementById('echart1'));
            // 绘制图表
            var option;
            var data = [
              {
                name: '范围二',
                children: [
                  { name: '1#办公', value: 2411.5275 },
                  { name: '2#宾馆', value: 846.150 },
                  { name: '3#宾馆', value: 1692.300 }
                ]
              },
              {
                name: '范围一',
                children: [
                  { name: '1#办公', value: 101.0 },
                  { name: '2#宾馆', value: 101.0 },
                  { name: '3#宾馆', value: 202.0 }
                ]
              }
            ];
            option = {
              series: {
                type: 'sunburst',
                emphasis: {
                  focus: 'ancestor'
                },
                data: data,
                radius: [0, '90%'],
                label: {
                  rotate: 'radial'
                }
              }
            };
            option && myChart.setOption(option);


            let myChart2 = this.$echarts.init(document.getElementById('echart2'))
            var option2;
            var data2 = {'project': ['本项目', '超高层项目2', '超高层项目3', '超高层项目4'],
                         'carbon': [5923.050000000001, 12936.0, 26350.0, 18572.487830000002],
                         'cui': [74.03812500000001, 81.1381708, 107.8081352, 61.79557762]
                         }
            option2 = {
              tooltip: {
                trigger: 'axis',
                axisPointer: {
                  type: 'cross',
                  crossStyle: {
                    color: '#999'
                  }
                }
              },
              toolbox: {
                feature: {
                  dataView: { show: true, readOnly: false },
                  magicType: { show: true, type: ['line', 'bar'] },
                  restore: { show: true },
                  saveAsImage: { show: true }
                }
              },
              legend: {
                data: ['碳排放', '单位面积碳排放']
              },
              xAxis: [
                {
                  type: 'category',
                  data: data2.project,
                  axisPointer: {
                    type: 'shadow'
                  }
                }
              ],
              yAxis: [
                {
                  type: 'value',
                  name: '碳排放 tCO2',
                  min: 0,
                  max: 30000,
                  interval: 5000,
                  axisLabel: {
                    formatter: '{value}'
                  }
                },
                {
                  type: 'value',
                  name: '单位面积碳排放 kgCO2/sqm',
                  min: 0,
                  max: 120,
                  interval: 20,
                  axisLabel: {
                    formatter: '{value}'
                  }
                }
              ],
              series: [
                {
                  name: '碳排放',
                  type: 'bar',
                  tooltip: {
                    valueFormatter: function (value) {
                      return value + ' tCO2';
                    }
                  },
                  data: [
                          {
                            value: data2.carbon[0],
                            itemStyle: {
                              color: '#91cc75'
                            }
                          }
                        ].concat(data2.carbon.slice(1))
                },
                {
                  name: '单位面积碳排放',
                  type: 'line',
                  yAxisIndex: 1,
                  tooltip: {
                    valueFormatter: function (value) {
                      return value + ' kgCO2/sqm';
                    }
                  },
                  data: data2.cui
                }
              ]
            };
            option2 && myChart2.setOption(option2);

            let myChart3 = this.$echarts.init(document.getElementById('echart3'))
            var option3;
            var data3 = {'buildingtype': ['商业办公(集中空调系统)', '宾馆(五星级)'],
                         'low': [85.0, 160.0],
                         'high': [70.0, 135.0],
                         'carbonintensity': [50.76, 112.82],
                         'between': [15.0, 25.0]},
            option3 = {
                tooltip: {
                  trigger: 'axis',
                  axisPointer: {
                    type: 'cross',
                    crossStyle: {
                      color: '#999'
                    }
                  }
                },
                toolbox: {
                  feature: {
                    dataView: { show: true, readOnly: false },
                    magicType: { show: true, type: ['line', 'bar'] },
                    restore: { show: true },
                    saveAsImage: { show: true }
                  }
                },
                legend: {
                  data: ['引导值','约束值', '本项目']
                },
                xAxis: [
                  {
                    type: 'category',
                    data: data3.buildingtype,
                    axisPointer: {
                      type: 'shadow'
                    }
                  }
                ],
                yAxis: [
                    {
                      type: 'value',
                      name: '单位面积碳排放 kgCO2/sqm',
                      min: 0,
                      max: 200,
                      interval: 50,
                      axisLabel: {
                        formatter: '{value}'
                      }
                    }
                ],
                series: [
                  {
                      name: '约束值',
                      type: 'bar',
                      stack: 'A',
                      tooltip: {
                        valueFormatter: function (value) {
                          return value + ' tCO2';
                        }
                      },
                      data: data3.low
                  },
                  {
                      name: '引导值',
                      type: 'bar',
                      stack: 'A',
                      tooltip: {
                        valueFormatter: function (value) {
                          return value + ' tCO2';
                        }
                      },
                      data: data3.between
                  },
                  {
                    name: '本项目',
                    type: 'effectScatter',
                    yAxisIndex: 0,
                    tooltip: {
                      valueFormatter: function (value) {
                        return value + ' kgCO2/sqm';
                      }
                    },
                    data: data3.carbonintensity
                  }
                ]
              };
              option3 && myChart3.setOption(option3);
        },
  }
</script>
