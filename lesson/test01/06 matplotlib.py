import matplotlib.pyplot as plt
import numpy as np

x=[1,2,3,4]
y=[1,4,9,16]
plt.plot(x,y)

'''
axis：坐标轴范围
语法为axis[xmin, xmax, ymin, ymax]，
也就是axis[x轴最小值, x轴最大值, y轴最小值, y轴最大值]
'''
plt.axis([0, 6, 0, 20])

plt.show()


t = np.arange(0, 5, 0.2)
print(t)

# 线条1
x1 = y1 = t

# 线条2
x2 = x1
y2 = t ** 2

# 线条3
x3 = x1
y3 = t ** 3

# 3条线绘图
LineList = plt.plot(x1, y1,
                    x2, y2,
                    x3, y3)

# 用setp方法可以同时设置多条线条的属性
plt.setp(LineList, color='blue')
plt.show()

# 创建画纸，并选择画纸1
'''
等价于ax1=fig.add_subplot(211)
在画纸中，subplot()方法的括号里包括三个数字：
前两个数字代表要生成几行几列的子图矩阵，
第三个数字代表选中的子图位置。
'''
ax1 = plt.subplot(2, 1, 1)

# 在画纸1上绘图
plt.plot([1, 2, 3])

# 选择画纸2
ax2 = plt.subplot(2, 1, 2)
# 在画纸2上绘图
plt.plot([4, 5, 6])

plt.show()