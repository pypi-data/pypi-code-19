#声呐数据集，所有的变量是连续的,一般在0到1的范围。输出变量是一个字符串“M”和“R”岩石还是金属,它将需要转化为整数 1 和 0
import time
import pandas
import numpy
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

#初始化随机数生成器,以确保执行这段代码时,我们总是得到相同的随机数序列,有助 于调试
seed = 7
numpy.random.seed(seed)

#pandas 库来加载数据集,因为它很容易处理字符串(输出变量),而试图使用 NumPy 加载数据会更困难
#列向量分割成60输入变量(X)和1个输出变量(Y)
dataframe = pandas.read_csv("data/sonar.csv",header=None)#加载数据集
dataset = dataframe.values
X = dataset[:,0:60].astype(float)
Y = dataset[:,60]

#数据集中输出变量是字符串类型，必须将其转换为整数值 0 和 1
#可以使用从scikit-learn LabelEncoder类。这个类通过 fit() 函数获取整个数据集模型所需的编码,然后使用transform()函数应用编码来创建一个新的输出变量
encoder = LabelEncoder()
encoder.fit(Y)
encoderd_Y = encoder.transform(Y)

#让我们开始定义一个函数用于创建我们的基准模型。我们的模型会有一个与输入层神经元相同数量（60个）的全连接隐藏层。这是一个建立神经网络时很好的默认起点。
#权值初始化使用一个小的高斯随机数,激活函数使用 ReLU 函数。输出层包含单个神经元以作出预测。使用 sigmoid 激活函数是为了产生一个0到1的范围的概率,这可以很容易地和自动地转换为离散类型的值。
#最后,我们使用对数损失函数(binary_crossentropy)训练,这是二元分类问题会优先使用的损失函数。模型还使用高效的 Adam 优化器来做梯度下降,精度指标将模在型训练时收集。

#基准模型
def creat_baseline():
    #creat model
    model = Sequential()
    model.add(Dense(60,input_dim=60,kernel_initializer='normal',activation='relu'))
    model.add(Dense(1,kernel_initializer='normal',activation= 'sigmoid'))
    #compile model
    model.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy'])
    return model

#我们将使用scikit-learn的k-fold交叉评估模型验证。这是一个重采样进行模型性能评估的技术。它通过把数据分成k个部分,训练模型在所有k部分中分出一个作为测试集对模型的性能进行评估。
# 这个过程重复 k 次的平均分数作为所有构造模型稳健的性能评估。它是分层的,这意味着它将关注输出值并试图平衡K份数据中每个类别的势利数量。
#在 scikit-learn 中使用 Keras 的模型,我们必须使用 KerasClassifier 进行包装。这个类起到创建并返回我们的神经网络模型的作用。它需要传入调用 fit()所需要的参数,比如迭代次数和批处理大小。

#evaluate model with standardized dataset
# start_time = time.time()
# estimator = KerasClassifier(build_fn=creat_baseline(),epochs=100,batch_size=5,verbose=0)
# kfold = StratifiedKFold(n_splits=10,shuffle=True,random_state=seed)
# results = cross_val_score(estimator,X,encoderd_Y,cv=kfold)
# print("Baseline:%.2f%% (%.2f%%)" % (results.mean()*100,results.std()*100))
# end_time = time.time()
# print("用时：",end_time-start_time)
start_time = time.time()
numpy.random.seed(seed)
estimators = []
estimators.append(('standardize',StandardScaler()))
estimators.append(('mlp',KerasClassifier(build_fn=creat_baseline(),epochs =100,batch_size = 5,verbose = 0)))
pipeline = Pipeline(estimators)
kfold = StratifiedKFold(n_splits=10,shuffle=True,random_state=seed)
results = cross_val_score(pipeline,X,encoderd_Y,cv=kfold)
print("Standardized: %.2f%% (%.2f%%)" % (results.mean()*100,results.std()*100))
end_time = time.time()
print("用时：",end_time-start_time)
# estimator = KerasClassifier(build_fn=creat_baseline(),epochs=100,batch_size=5,verbose=0)
# kfold = StratifiedKFold(n_splits=10,shuffle=True,random_state=seed)
# results = cross_val_score(estimator,X,encoderd_Y,cv=kfold)
# print("Baseline:%.2f%% (%.2f%%)" % (results.mean()*100,results.std()*100))
# end_time = time.time()
# print("用时：",end_time-start_time)

# 如何加载和准备数据
# 如何创建一个基线神经网络模型
# 如何使用scikit-learn 和 k-fold 交叉验证评估Keras模型
# 数据准备如何提升你的模型的性能
# 如何调整网络拓扑结构可以提高模型的性能实验

