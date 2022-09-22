# 自定义指令的使用

*要进行指令的自定义, 您必须会熟练使用正则表达式, 并默认您对 yaml 有以一定的了解*

以添加管理员为例,其指令正则表达式为:`^{commandpre}addadmin\s*(\d+)\s*$`

只能修改`^{commandpre}` 后面的部分，`{commandpre}`为自定义的指令前缀,修改完指令主体会自动拼接指令前缀

请严格保持括号顺序,不要增加，也不要减少，修改顺序和变更数量会导致程序出错

**yaml 与 python 的简单互转**

**注意缩进,冒号后面要有空格 !!**
```yaml
# dict  <=> yaml
# python:
# dict(name='nekorabi',like='lux',age=20,hobby=['sleep','code'])
# yaml:
name: nekorabi
like: lux
age: 20
hobby:  
    -'sleep'
    -'code'
```

以雀魂模块的雀魂月报为例简单说明

```yaml
majsoul:
  qhyb: (qhyb|雀魂月报)\s*([\w_、,\.，@。\'\"!]+)\s*([34])?\s*([0-9]{4})?[-]?([0-9]{1,2})?\s*$
```

指令触发,进行处理时,会进行匹配
第一个参数为 <font color='green'>触发词</font> ,可以在括号内填入多个触发词,使用 `|` 进行分割,第二个参数为 <font color='blue'>玩家名
</font> ,第三个参数为查询类型,是三麻还是四麻 ( 可不填,默认四麻 ),第四第五个参数分别为年月 ( 时间参数 ),
可不填,默认为当前月份 

**<font color="red">因此,保持括号的顺序和数量是很重要的</font>**

