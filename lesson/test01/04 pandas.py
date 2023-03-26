# 导入NumPy包，并且命名为np
import numpy as np
# 导入Pandas包，命名为pandas
import pandas as pd

'''
NumPy中一维数组的格式是Array，Pandas中的则是Series
（1）Array与List的区别：NumPy数组Array中的每一个元素都必须是同一种数据类型，而列表List中的元素可以是不同的数据类型。
（2）Array与Series的区别：Series有索引，可以用index来定义这个索引，方便索引后面的元素。Array则没有。
'''

# 1. 定义一组数据array([  ])
a=np.array([2,3,4,5,6])
# 2. 查询
print(a[0])
# 3. 切片
print(a[1:3])
# 4.数据类型dtype
print(a.dtype)

# 1. 平均值
print(a.mean())
# 2. 标准差
print(a.std())
b=a*3
print(b)

# 1.定义股票数组
stocks=pd.Series([54.74,190.9,173.14,1050.3,181.86,1139.49,],
			  index=['腾讯','阿里巴巴','苹果','谷歌','Facebook','亚马逊'])
# 2.查看一维数组Series的统计特性
print(stocks.describe())
# 3.iloc查询
print(stocks.iloc[0])
# 4.loc查询
print(stocks.loc['Facebook'])

'''
跟NumPy一维数组Array一样，Pandas的Series也支持向量运算，但只能与索引值相同的值相加。
'''
# 1. 向量运算，向量相加
s1=pd.Series([1,2,3,4],index=['a','b','c','d'])
s2=pd.Series([10,20,30,40], index=['a','b','e','f'])
s3=s1+s2
print(s3)
print(s3.dropna())
s4=s1.add(s2,fill_value=0)
print(s4)

'''
二维数组
'''
a=np.array([
	[1,2,3,4],
	[5,6,7,8],
	[9,10,11,12]
])
print('第1行的值是：', a[0], a[0,:])
print('第2列的值是：', a[:,1])
print('第2行第3列的值是：', a[1,2])
print('计算平均值：',a.mean())
print('按行分组计算：',a.mean(axis=1))
print('按列分组计算：',a.mean(axis=0))

'''
Pandas二维数组DataFrame
（1）数组中的每一列都可以是不同类型，方便表示Excel中的数据。
（2）数组中的每一行/列都有一个索引表格，类似于一维数组Series，使得常见的表格数据很容易制作。
'''
# 首先定义一个字典，映射列名于相应列的值。
salesDict={
	'日期':['2018-08-01','2018-08-02','2018-08-03'],
	'开盘价':['001616528','001616528','0012602828'],
	'最高价':[236701,236701,236701],
	'收盘价':['强力VC银翘片','清热解毒口服液','感康'],
	'最低价':[6,1,2],
	'成交量':[82.8,28,16.8],
}
# 然后导入有序字典,将salesDict定义成有序字典
from collections import OrderedDict
salesOrderedDict=OrderedDict(salesDict)
# 最后传入数据框：传入字典，列名
salesDf=pd.DataFrame(salesOrderedDict)
print(salesDf)

# 1.构建查询条件
querySer=salesDf.loc[:,'最低价']>2
# 2.查看数组类型
print(type(querySer))
# 3. 查看判断结果
print(querySer)
# 4.应用查询条件来筛选出结果为True的行
print(salesDf.loc[querySer,:])