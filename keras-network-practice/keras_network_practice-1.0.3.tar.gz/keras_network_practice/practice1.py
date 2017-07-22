#MNIST手写数字识别，MNIST数据集是一个手写体数据集
from __future__ import print_function
import keras
from keras.models import Sequential#Sequential类，可以封装各种神经网络层，包括Dense全连接层，Dropout层，Cov2D 卷积层，等等
from keras.datasets import mnist#mnist数据源
from keras.layers import Dense,Dropout,Flatten
from keras.layers import Conv2D,MaxPooling2D
from keras import backend as K

#准备训练集和测试集，以及一些重要参数
#batch_size太小会导致训练慢，过拟合等问题，太大会导致欠拟合。所以要适当选择
batch_size = 128
#0-9手写数字一共10个类别
num_classes = 10
#12次完整迭代
epochs = 12

#输入的图片是28*28像素的灰度图
img_rows,img_cols = 28,28

#训练集，测试集收集非常方便
(x_train,y_train),(x_test,y_test) = mnist.load_data()

# keras输入数据有两种格式，一种是通道数放在前面，一种是通道数放在后面，
# 其实就是格式差别而已
if K.image_data_format() == 'channels_first':
    x_train = x_train.reshape(x_train.shape[0],1,img_rows,img_cols)
    x_test = x_test.reshape(x_test.shape[0],1,img_rows,img_cols)
    input_shape = (1,img_rows,img_cols)
else:
    x_train = x_train.reshape(x_train.shape[0],img_rows, img_cols,1)
    x_test = x_test.reshape(x_test.shape[0],img_rows, img_cols,1)
    input_shape = (img_rows, img_cols,1)

#把数据变成float32更精确
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /=255
x_test /=255
print('x_train shape:',x_train.shape)
print(x_train.shape[0],'train samples')
print(x_test.shape[0],'test samples')

#把类别0-9变成2进制，方便训练
y_train = keras.utils.np_utils.to_categorical(y_train,num_classes)
y_test = keras.utils.np_utils.to_categorical(y_test,num_classes)

model = Sequential()
#加上一个2D卷积层， 32个输出（也就是卷积通道），激活函数选用relu，
# 卷积核的窗口选用3*3像素窗口
model.add(Conv2D(32,(3,3),activation="relu",input_shape=input_shape))
#64个通道的卷积层
model.add(Conv2D(64,(3,3),activation="relu"))
#2*2像素的池化层activation="relu"))

model.add(MaxPooling2D(pool_size=(2,2)))
#对于池化层的输出，采用0.35概率的Dropout
model.add(Dropout(0.35))
# 展平所有像素，比如[28*28] -> [784]
model.add(Flatten())

# 对所有像素使用全连接层，输出为128，激活函数选用relu
model.add(Dense(128,activation="relu"))
#采用0.5的Dropout
model.add(Dropout(0.5))
#对刚才Dropout的输出采用softmax激活函数，得到最后结果0-9
model.add(Dense(num_classes,activation="softmax"))

#模型我们使用交叉熵损失函数，最优化方法选用Adadelta
model.compile(loss=keras.metrics.categorical_crossentropy,optimizer=keras.optimizers.Adadelta(),metrics=['accuracy'])#metrics：列表，包含评估模型在训练和测试时的网络性能的指标
#训练
model.fit(x_train,y_train,batch_size=batch_size,epochs=epochs,verbose=1,validation_data=(x_test,y_test))#verbose：日志显示，0为不在标准输出流输出日志信息，1为输出进度条记录，2为每个epoch输出一行记录
#计算预测准确率
score = model.evaluate(x_test,y_test,verbose=0)
print('Test loss:',score[0])
print('Test accuracy:',score[1])