**【功能描述】**

- 指定源ip列表文件，并发ping所有ip, 输出监测时间端内分析结果

**【使用方法】**

Function|Detail|Example
---|---|--
[ -f ]|set source file     |  `sh fping2.sh ip.lst`
[exit]| use ctrl+c|`ctrl+c`

**【注意】**

- 自带fping,无需安装

**【最近更新】**

- 删除了Unreachable的WARNING打印，防止日志过多影响分析
- 增加了头包不可达和尾包不可达的检测
- 单个ICMP报文超时时间调整为1s. (如果超过1s后收到以前的报文会有WARNING打印)
- 增加了报文乱序场景的WARNING打印，可以在detail文件里查看，方便定位
- 限制IP个数为200，限制ping间隔为0.05秒
- 2018年4月13日14:10:23
