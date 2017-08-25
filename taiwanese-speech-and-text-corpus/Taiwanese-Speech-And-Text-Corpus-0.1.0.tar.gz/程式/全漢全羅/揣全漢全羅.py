import gzip
from os.path import isfile
import pickle
from 臺灣言語工具.斷詞.拄好長度辭典揣詞 import 拄好長度辭典揣詞
from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from 臺灣言語工具.語言模型.KenLM語言模型 import KenLM語言模型
from 臺灣言語工具.斷詞.語言模型揀集內組 import 語言模型揀集內組
from 程式.全漢全羅.做辭典 import 做
from 程式.全漢全羅.語料路徑 import 語料路徑
from 臺灣言語工具.解析整理.文章粗胚 import 文章粗胚
from 臺灣言語工具.音標系統.閩南語.通用拼音音標 import 通用拼音音標


# 語法錯誤表=[('niunn','niu'),('min','bin'),('ian','iam'),('ghian','giam'),('cian','tshiam'),
#     ('gian','kian'),('hiat','hiak'),('zian','ziam'),('ming','bing'),('mong','bong'),
#     ('puo','phoo'),('huo','hoo'),('s','si'),('z','tsi')]
音標錯誤表 = [
    ('niunn', 'niu'), ('min', 'bin'),
    ('miann', 'mia'), ('mong', 'bong'), ('ming', 'bing'),
    ('nq', 'ng'),
    # 拍無著的，有查過原來應該是按怎
    #     ('pian','piann'),('ghian','ghia'),
    #     ('hiat','hiah'),
    #     ('ian','en'),('cian','ciam'),
    #     ('hian','hiam'),('lian','liang'),('tian','tiann'),
    #     ('puo','po'),('huo','hu'),
    #     ('huei','hue'),('ton','to'),('nin','ni'),('ie','iap'),('loi','li'),('guk','gut'),
    #     ('kuang','kang'),
    #     ('men','me'),
    #     ('n','na'),
    # 有變iann，嘛有iam，iann較濟，予伊較袂汙染著
    #     ('gian','giann'),('zian','zinn'),
    # z佮s後擺無一定是i，但是i較濟，予伊平均
    #     ('s','si'),('z','zi')
]


class 揣全漢全羅:
    辭典揣詞 = 拄好長度辭典揣詞()
    揀集內組 = 語言模型揀集內組()

    def __init__(self):
        if not isfile(語料路徑.斷詞典()) or not isfile(語料路徑.斷詞語言模型()):
            self.辭典 = 做()
        else:
            with gzip.open(語料路徑.斷詞典(), 'rb') as f:
                self.辭典 = pickle.load(f)
        self.連詞 = KenLM語言模型(語料路徑.斷詞語言模型())

    def 通用處理做口語調臺羅(self, 通用口語調音標):
        新音標 = 通用口語調音標.replace('_', '-').strip('-').replace(',', ' ').strip()
        新音標 = 文章粗胚.數字英文中央全加分字符號(新音標)
        for 錯, 著 in 音標錯誤表:
            新音標 = 新音標.replace(錯, 著)
        新音標 = 文章粗胚.建立物件語句前處理減號(通用拼音音標, 新音標)
        音標句物件 = 拆文分析器.建立句物件(新音標)
        return 音標句物件.轉音(通用拼音音標)

    def 變調臺羅轉本調臺羅(self, 變調句物件):
        接起來句物件 = 拆文分析器.建立句物件('')
        for 詞 in 變調句物件.網出詞物件():
            揣詞結果 = self.辭典揣詞.揣詞(self.辭典, 詞)
            揣著句物件 = 揣詞結果
            接起來句物件.內底集.extend(揣著句物件.內底集)
        for 集物件 in 接起來句物件.內底集:
            for 組物件 in 集物件.內底組:
                for 字物件 in 組物件.篩出字物件():
                    if 字物件.型 == '-':
                        字物件.音 = '-'
                    else:
                        try:
                            字物件.型, 字物件.音 = 字物件.型.split('｜')
                        except:
                            # 辭典無這音
                            # print('{} 無佇語料出現'.format(字物件))
                            字物件.音 = 字物件.型
        結果 = self.揀集內組.揀(self.連詞, 接起來句物件)
        return 結果
