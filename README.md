# Chinese Holiday 中国节假日日历插件
## 日历及节假日显示组件
可以显示中国节假日, 周年, 纪念日, 生日等(支持农历和阴历)日历插件, 同时, 支持计算某个日期和时间已经过去了N年N月N天N小时N秒.


# 安装
## HACS 安装(建议使用HACS安装和配置)
0. 手动添加自定义存储库 https://github.com/Crazysiri/chineseholiday 
1. HACS 添加集成 > 搜索 ```中国节假日日历```，点击下载

配合此集成的[前端卡片](https://github.com/Crazysiri/chineseholiday_card)

## 手动安装
下载 /custom_components/chineseholida 下的所有文件
复制到 \config\custom_components 
重启Home Assistant
此时应该可以在 配置 > 设备与服务 > 添加集成内搜索"chineseholiday" 或者 "中国节假日日历插件"

## 安装卡片，使用以下配置：

```
在页面添加下面的源
resources:
  - type: module
    url: /local/custom-lovelace/ch_calendar-card/ch_calendar-card.js

在添加卡片, 可以直接找到中国节假日日历的卡片, 或者 手动添加卡片, 填写下面的卡片配置代码

卡片配置
  - type: 'custom:ch_calendar-card'
    entity: sensor.holiday                                        
    icons: /local/custom-lovelace/ch_calendar-card/icons/

```

# 配置：
在configuration.yaml文件里,添加你的各种日期, 重启生效.

```
sensor:
  - platform: chineseholiday
    name: holiday
    solar_anniversary:
      '0121':
        - aa生日
        - cc生日
      '20200220': #这样配置会在显示的时候略有不一样，会以 bb生日(1岁) 的形式显示, 文案不包含 ‘生日’ 的统一显示为周年 xx纪念日（1周年）。
        - bb生日  #卡片前端aa生日(1岁)
        - aa和bb结婚纪念日 #卡片前端显示xx纪念日（1周年）
    lunar_anniversary:
      '0321':
        - aa农历生日
    calculate_age: #通过配置一个 'aa和bb结婚周年' '2022-10-10 10:23:10'(过去的时间)，1. 自动生成未来的时间将近的周年纪念日, 2.计算这个时间已经过去了N年N月N天N小时N秒
        - date: '2022-10-10 10:23:10'
          name: 'aa和bb结婚周年'
    notify_script_name: 'test' #调用脚本名字
    notify_times: #早上9点10分调用 13:00:00 下午1点调用
        - "09:10:00" 
        - "13:00:00"
    notify_principles: #调用脚本规则
      '14|7|1': #未来某个日期（下面每个date字段对应）离现在还有 14 天 7天 1天时调用脚本
        - date: "0101" #需要调用脚本的日期
          solar: False ##没填solar的默认为True 即阳历. false就是阴历, true是阳历 
        - date: "0102"  #需要调用脚本的日期 solar 不写 默认为True 即阳历
      '0': #0即为当天调用
        #*下面两种是特殊情况采用name，只有父亲节和母亲节 ，也就是填了name就不要填date，填name的只有这两种情况
        - name: "母亲节"
        - name: "父亲节"

```


# 更新


+ #### 2025-7-8 01:43:41 更新

适配Home Assistant core 2025.7.1

Home Assistant 内核更新到2025.7.1后,集成无法加载.

报错:
```
Version v0.2.0.6 will be downloaded

When downloaded, this will be located in '/config/custom_components/chineseholiday'
Remember that you need to restart Home Assistant before changes to integrations (custom_components) are applied.

Need a different version?
It is not advised to use this section to do a rollback, restore a backup instead.

Release
v0.2.0.6
<Plugin Crazysiri/chineseholiday> Repository structure for v0.2.0.6 is not compliant

```
