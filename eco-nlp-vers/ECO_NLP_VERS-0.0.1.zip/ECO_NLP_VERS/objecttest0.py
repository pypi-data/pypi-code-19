from ECO_NLP_workdirectory import SnowNLP0

from ECO_NLP_workdirectory import sentiment0

#negaddress = 'C:/Users/asus/Desktop/Quant@Fund/ECO_NLP_workdirectory/material_package/noeco_txts.txt'
#posaddress = 'C:/Users/asus/Desktop/Quant@Fund/ECO_NLP_workdirectory/material_package/eco_news.txt'

#saveaddress = 'C:/Users/asus/Desktop/Quant@Fund/ECO_NLP_workdirectory/sentiment0/save_eco.marshal'

#sentiment0.train(negaddress,posaddress)
#sentiment0.save(saveaddress)


test_text1 = u'这个东西很不错，我很看好他'
test_text2 = u'我觉得这个东西挺糟糕的，一点也不好'

test_text3 = u'唐嫣晒出一张拍立得照片，唐嫣背对大海对镜头甜笑，宽宽的帽檐和大大的墨镜遮住半张俏脸，但挡不住她微翘的嘴角透露出的好心情。'
test_text4 = u'2017年7月25日，群兴玩具公告，因资产计划管理方光大证券(15.460, 0.17, 1.11%)通知“光证资管-浦发银行(13.430, 0.07, 0.52%)-群兴1号集合资产管理计划”到期后不续展，故控股股东群兴投资于2017年7月24日通过大宗交易方式减持其通过资产管理计划所持公司股份1647万股（减持均价8.42元/股），占公司总股本2.8%。。'
test_text5 = u'黄婷婷的粉丝说，她是一个养成感十足的偶像，几乎是在粉丝眼皮子底下成长起来的。'

s1 = SnowNLP0(test_text1)
s2 = SnowNLP0(test_text2)
s3 = SnowNLP0(test_text3)
s4 = SnowNLP0(test_text4)
s5 = SnowNLP0(test_text5)
print(test_text1,'\n','s1.sentiments = ',s1.sentiments,'\n')
print(test_text2,'\n','s2.sentiments = ',s2.sentiments,'\n')
print(test_text3,'\n','s3.sentiments = ',s3.sentiments,'\n')
print(test_text4,'\n','s4.sentiments = ',s4.sentiments,'\n')
print(test_text5,'\n','s5.sentiments = ',s5.sentiments,'\n')
