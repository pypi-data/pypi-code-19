#加载数据,使用的是皮马印第安人糖尿病数据集（描述了病人医疗记录和他们是否在五年内发病），二分类问题
import numpy
from keras.models import Sequential
from keras.layers import Dense#全连接层
# fix random seed for reproducibility
seed = 7#初始化随机数发生器及其种子
numpy.random.seed(seed)#设置相同的seed，每次生成的随机数相同

# load pima indians dataset
dataset = numpy.loadtxt("data/pima-indians-diabetes.csv.txt",delimiter=",")
#split into input(x) and output(y) variables
X = dataset[:,0:8]
Y = dataset[:,8]

#creat model
model = Sequential()
model.add(Dense(12,input_dim=8,activation='relu',kernel_initializer='uniform'))
model.add(Dense(8,activation='relu',kernel_initializer='uniform'))
model.add(Dense(1,activation='sigmoid',kernel_initializer='uniform'))


#compile model
model.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy'])#binary_crossentropy:对数损失函数；adam：梯度下降算法;这是一个分类问题, 所以我们会收集和汇报分类的准确率作为度量指标

#Fit the model
model.fit(X,Y,epochs=70,batch_size=20,verbose=1)#迭代150次、批处理大小为10,


#evaluate the model
scores  = model.evaluate(X,Y)
print("%s: %.2f%%" % (model.metrics_names[1],scores[1]*100))

#calculate predictions
#predictions = model.predict(X)

#round predictions
#rounded = [numpy.around(x) for x in predictions]
#print(rounded)