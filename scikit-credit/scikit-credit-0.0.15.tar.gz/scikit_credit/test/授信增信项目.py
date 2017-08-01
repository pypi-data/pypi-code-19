# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import scipy
from scipy import sparse
from sklearn.pipeline import make_pipeline
from sklearn.grid_search import GridSearchCV
import matplotlib.pyplot as plt
import scikit_credit

plt.style.use('ggplot')

# transformers for category variables
from sklearn.preprocessing import LabelBinarizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder


# transformers for numerical variables
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import Normalizer


# transformers for combined variables
from sklearn.decomposition import PCA
from sklearn.preprocessing import PolynomialFeatures


# user-defined transformers
from sklearn.preprocessing import FunctionTransformer


# classification models
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression


# evaluation
from sklearn.metrics import scorer

from sklearn.linear_model import LogisticRegression


# In[2]:

df = pd.read_csv(u'/home/jiyue/qddata/dm_tmp_user_shouxinzengxin_d4.csv', sep='\t')


# In[4]:

df.drop(['order_time', 'gender', 'add_info_time'], axis=1, inplace=True)


# In[5]:

df.drop_duplicates(inplace=True)

from scikit_credit import plot

df.drop(
    ['score', 'operatorvoices_total_time_avg_everyday_6m', 'ss_bank_avg_income_6m', 'ss_operatorbasic_extendjointdt',
     'operatorbills_billmonthamt_avg_6m'], axis=1, inplace=True)


# In[10]:

df.fillna(0, inplace=True)




# In[14]:

from scikit_credit import encoder



# # 首先进行适当的降采样

# In[15]:

good_bad_odd = 10

total_nums = df.shape[0]
bad_nums = df[df['label'] == 1].shape[0]
good_nums = df[df['label'] == 0].shape[0]

origin_g_b_rate = (1.0 * good_nums / bad_nums)  # 原始好坏样本比例
df_good_users = df[df['label'] == 0].sample(bad_nums * good_bad_odd)
df_bad_users = df[df['label'] == 1]

print df_good_users.shape[0]
print df_bad_users.shape[0]


# In[16]:

frames = [df_good_users, df_bad_users]
df = pd.concat(frames)

y_src = df['label']
X_src = df.drop(['label'], axis=1)

woe_encoder = encoder.WoeEncoder(bin_width=8)
woe_encoder.fit_transform(X_src.values, y_src.values)


# In[33]:

binned_X = woe_encoder._X_binned
print binned_X.max()
print binned_X.min()

# In[31]:

df_binned_X = pd.DataFrame(data=binned_X, columns=X_src.columns.values)
df_binned_X['id_age'].value_counts()


# In[20]:

# df_binned_X['ss_bank_avg_income_6m'] =  df_binned_X['ss_bank_avg_income_6m'].astype('category')
# df_binned_X['ss_operatorbasic_extendjointdt'] =  df_binned_X['ss_operatorbasic_extendjointdt'].astype('category')
# df_binned_X['operatorbills_billmonthamt_avg_6m'] =  df_binned_X['operatorbills_billmonthamt_avg_6m'].astype('category')
# df_binned_X['operatorvoices_total_time_avg_everyday_6m'] =  df_binned_X['operatorvoices_total_time_avg_everyday_6m'].astype('category')
df_binned_X['id_age'] = df_binned_X['id_age'].astype('category')
# df_binned_X['score'] =  df_binned_X['score'].astype('category')



# In[21]:

df_binned_dummy_x = pd.get_dummies(df_binned_X)

from sklearn.metrics import confusion_matrix
from sklearn.metrics import recall_score, precision_score, accuracy_score, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split, cross_val_predict, StratifiedKFold, \
    KFold
from sklearn.dummy import DummyClassifier
from sklearn.metrics import roc_curve, auc, roc_auc_score, accuracy_score

dummy_classifier = DummyClassifier(random_state=0, strategy='uniform')
from sklearn.metrics import recall_score, precision_score, accuracy_score, roc_auc_score

lr = LogisticRegression()
total = 0
fpr_sum, tpr_sum = 0, 0

X_train, X_test, y_train, y_test = train_test_split(df_binned_dummy_x.values, y_src)
print y_src.value_counts()

lr.fit(X_train, y_train)
rf_predict = lr.predict(X_test)
rf_predict_proba = lr.predict_proba(X_test)[:, 1]

print 'rf:recall:{},precision:{},accuracy:{},roc_auc:{}'.format(recall_score(y_test, rf_predict),
                                                                precision_score(y_test, rf_predict),
                                                                accuracy_score(y_test, rf_predict),
                                                                roc_auc_score(y_test, rf_predict_proba)
                                                                )

fpr, tpr, thresholds = roc_curve(y_test, rf_predict_proba)
coef = lr.coef_[0]
columns = df_binned_dummy_x.columns.values

plt.figure()
cf = confusion_matrix(y_test, rf_predict)
from scikit_credit import plot

plot.plot_confusion_matrix(cf, ['0', '1'])
plt.show()


def get_column_name(column):
    column_arr = column.split('_')
    num = str(column_arr[len(column_arr) - 1])
    return column[:-len(num) - 1]


print len(columns), columns
print woe_encoder._binned_range
with open('/home/jiyue/Desktop/output_encoding', 'w') as f:
    index = 0
    # fea_idx是特征索引,features_list是每个特征的分箱
    for fea_idx, features_list in enumerate(woe_encoder._binned_range):
        for binned_index, feature_item_range in enumerate(features_list):
            col_name = get_column_name(columns[index])
            f.write(col_name + '$' + str(int(feature_item_range[0]))
                    + '~' + str(int(feature_item_range[1]))
                    + '  ' + str(coef[index])
                    + ' ' + str(woe_encoder._woe[binned_index][fea_idx])
                    + '\n')

            print binned_index, feature_item_range, index, columns[index]
            index += 1
    print index



# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:
