import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl


# 计算n日移动均线
def moving_average(a,n=5):
    # cumsum累加
    ret = np.cumsum(a,dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n-1:]/n

def data_gen(size=50,low=20,high=30):
    np.set_printoptions(precision=2)
    data_1 = np.random.rand(size)

    # print("=================# 生成随机整数数组========================")
    data_2 = np.random.randint(low,high,size=size)
    # print(data_2)
    # print("=================# 生成随机小数数组========================")
    data_3 = data_1 + data_2
    data = np.around(data_3,decimals=2)
    return data

def data_show(data):
    max_index = np.argmax(data)
    max_value = data[max_index]
    print("=================# 最大数========================")
    print("位置: %d,值：%d" % (max_index,max_value))
    min_index = np.argmin(data)
    min_value = data[min_index]
    print("=================# 最小数========================")
    print("位置: %d,值：%d" % (min_index,min_value))

    print("=================# 移动均线数组========================")
    data_moving = moving_average(data)
    print(data_moving)

    print("=================# 画图========================")
    # 生成1-51的数组
    x = np.arange(1,51,1)
    plt.plot(x,data,"--*r")

    # 描出最大最小点
    show_max = '[key:' + str(max_index) + ' value:' + str(round(max_value,1)) + ']'
    plt.annotate(show_max,xytext=(max_index,max_value),xy=(max_index,max_value))
    show_min = '[key:' + str(min_index) + ' value:' + str(round(min_value,1)) + ']'
    plt.annotate(show_min,xytext=(min_index,min_value),xy=(min_index,min_value))

    # 移动均线
    x_average = np.arange(4,50,1)
    plt.plot(x_average,data_moving,"b")

    mpl.rcParams['font.sans-serif']=['SimHei']
    plt.title("行情及五日均线")
    plt.savefig("./20230312.png")
    plt.show()