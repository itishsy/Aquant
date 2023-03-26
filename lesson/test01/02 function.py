
'''
定义函数
函数功能：两个数相加
输入：x,y是两个要输入的数字
输出：z是两个数相加的和，用return键来导出
'''

# 1.定义函数
def add(x,y):
  z=x+y
  return z

# 2.调用函数
a=1
b=2
c=add(a,b)
print('a和b相加为',c)

#  1.简单条件判断
# 《摔跤吧，爸爸》，豆瓣评分
scoreNum=9.1
if scoreNum >=8 :
  print ('我要看这部电影')
else:
  print ('电影太烂，不想看')

# 2. 多个条件判断
age = int(input ('请输入你家狗狗的年龄，按Enter键获取计算结果：'))
if age < 0:
  print('狗狗的年龄不能少于0岁')
elif age==1:
  print('相当于14岁的人')
elif age==2:
  print('相当于14岁的人')
else:
  human=22+(age -2)*5
  print('对应人类年龄：', human )

# 1.容器：一天中吃几次饭
eatList=[1,3,5]
# 循环
for i in eatList:
  j=i+2
  print(j)

# 2.对字典进行循环
'''
定义字典：6家公司(GAFATA) 的股票
key是公司名称，value是公司代码
'''

gafataDict={'腾讯':'HK:00700','阿里巴巴':'baba','苹果':'Apple','谷歌':'GOOGLE','Facebook':'fb','亚马逊':'amzn'}
# 将股票代码全部改成大写(upper)
# 注意用key，value
for key,value in gafataDict.items():
  newValue=value.upper()
  gafataDict[key]=newValue
print (gafataDict)
