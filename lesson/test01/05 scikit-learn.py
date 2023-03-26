import pandas as pd
import matplotlib.pyplot as plt
from collections import OrderedDict

examDict={
	'学习时间':[0.50,0.75,1.00,1.25,1.50,1.75,1.75,2.00,2.25,
		  2.50,2.75,3.00,3.25,3.50,4.00,4.25,4.50,4.75,5.00,5.50],
	'分数':    [10,  22,  13,  43,  20,  22,  33,  50,  62,
		  48,  55,  75,  62,  73,  81,  76,  64,  82,  90,  93]
}
# 然后变成有序字典，用OrderedDict()
examOrderDict=OrderedDict(examDict)

# 通过有序字典构建数据框pd.DataFrame
examDf=pd.DataFrame(examOrderDict)
print(examDf.head())

exam_X=examDf.loc[:,'学习时间']
exam_Y=examDf.loc[:,'分数']

plt.scatter(exam_X, exam_Y, color='b', label='exam indicator')
plt.xlabel('hours')
plt.ylabel('score')
# plt.show()

'''
建立训练数据和测试数据
交叉验证（Cross-validation）指的是在给定的建模样本中，拿出大部分样本建模型，留小部分样本用刚建立的模型进行预报。
train_test_split是交叉验证中常用的函数，
功能是从样本中按比例随机选取训练数据（train）和测试数据（test）。
'''
from sklearn.model_selection import train_test_split

#建立训练数据和测试数据,要按照下面的顺序
X_train, X_test, y_train, y_test= train_test_split(exam_X,exam_Y,train_size=0.8)
#输出数据大小
print('原始数据特征',exam_X.shape ,
	'，训练数据特征', X_train.shape ,
	'，测试数据特征',X_test.shape )

print('原始数据标签',exam_Y.shape ,
	'，训练数据标签', y_train.shape ,
	'，测试数据标签',y_test.shape )

#绘出训练和测试的散点图
plt.scatter(X_train, y_train, color='b',label='train indicator')
plt.scatter(X_test, y_test,color='red',label='test indicator')
#添加图标标签
plt.legend(loc=2)
plt.xlabel('Hours')
plt.ylabel('Score')
# plt.show()

'''
scikit-learn要求输入的特征必须是二维数组的类型，但是因为我们目前只有1个特征，
所以需要转换成二维数组的类型。
错误提示信息：Reshape your indicator either using array.reshape(-1,1)
if your indicator has a single feature
'''
#将训练数据特征和标签转换成二维数组n行×1列，用values.reshape（-1,1）
X_train=X_train.values.reshape(-1,1)
y_train=y_train.values.reshape(-1,1)

'''
开始训练模型，一共分为3步。
'''
#第1步：导入线性回归
from sklearn.linear_model import LinearRegression

# 第2步：创建模型，线性回归
model=LinearRegression()

# 第3步：训练模型
# fit()函数，传入第一个参数是训练数据的特征X，第二个参数是训练参数的标签y
model.fit(X_train, y_train)

# 建立最佳拟合线
a = model.intercept_
b = model.coef_
print('最佳拟合线，截距a=', a, '，回归系数b=', b)

#训练数据散点图
plt.scatter(X_train, y_train, color='b',label='train indicator')

# 训练数据的预测（通过机器学习sklearn中的Linear Regression,用model.predict）
y_train_pred=model.predict(X_train)

#绘制最佳拟合线图,线而不是散点，不用scatter，而用plot
plt.plot(X_train, y_train_pred, color='black', linewidth='3', label='best line')

# 添加图标标签
plt.legend(loc=2)
plt.xlabel('Hours')
plt.ylabel('Score')

#显示图函数show()
plt.show()

'''
评估模型
'''
# 1.相关系数：corr返回结果是一个数据框，存放的是相关系数矩阵
rDf=examDf.corr()
print('相关系数矩阵：',rDf)

# 2.转换矩阵
X_test=X_test.values.reshape(-1,1)
y_test=y_test.values.reshape(-1,1)

# 3线性回归的score方法得到的是决定系数R平方
#评估模型:决定系数R平方
print("线性回归的score:", model.score(X_test,y_test))

'''
逻辑回归（Logistic Regression）模型其实仅在线性回归的基础上，套用了一个逻辑函数
'''

'''
1．构建字典
'''

# 字典—有序字典—数据框
examDict2={
	'学习时间':[0.50,0.75,1.00,1.25,1.50,1.75,1.75,2.00,2.25,2.50,
		  2.75,3.00,3.25,3.50,4.00,4.25,4.50,4.75,5.00,5.50],
	'通过考试':[0,0,0,0,0,0,1,0,1,0,1,0,1,0,1,1,1,1,1,1]
}
examOrderdDict2=OrderedDict(examDict2)
examDf2=pd.DataFrame(examOrderdDict2)

# 1.提取特征和标签
exam_X2=examDf2.loc[:,'学习时间']
exam_Y2=examDf2.loc[:,'通过考试']

# 2.绘制散点图
plt.scatter(exam_X2, exam_Y2, color='b',label='exam indicator')

plt.xlabel('Hours')
plt.ylabel('Pass')
plt.show()

'''
2.建立训练数据和测试数据
'''
X_train2, X_test2, y_train2, y_test2=train_test_split(exam_X2,
									  exam_Y2,
									  train_size=0.8)

'''
3. 训练模型并且建立最佳拟合线。
'''

# 逻辑回归函数LogisticRegression
from sklearn.linear_model import LogisticRegression
model2=LogisticRegression()

X_train2=X_train2.values.reshape(-1,1)
model2.fit(X_train2, y_train2)

'''
4．评估模型。决定系数R平方为50%，代表着50%的考试成绩y的波动可以由回归线描述。
'''
X_test2=X_test2.values.reshape(-1,1)
#y_test2=y_test2.values.reshape(-1,1)
print("逻辑回归score:",model2.score(X_test2, y_test2))