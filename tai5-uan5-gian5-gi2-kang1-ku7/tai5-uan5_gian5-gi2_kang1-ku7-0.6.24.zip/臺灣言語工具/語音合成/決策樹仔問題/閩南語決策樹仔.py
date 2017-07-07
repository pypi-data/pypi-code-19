# -*- coding: utf-8 -*-
from 臺灣言語工具.語音合成.決策樹仔問題.公家決策樹仔 import 公家決策樹仔
from 臺灣言語工具.語音合成.生決策樹仔問題 import 生決策樹仔問題
from 臺灣言語工具.音標系統.閩南語.臺灣閩南語羅馬字拼音轉音值模組 import 臺灣閩南語羅馬字拼音對照音值聲母表
from 臺灣言語工具.音標系統.閩南語.臺灣閩南語羅馬字拼音轉音值模組 import 臺灣閩南語羅馬字拼音對照音值韻母表
import itertools
import os
import sys


class 閩南語決策樹仔(公家決策樹仔):
    _生問題 = 生決策樹仔問題()
    聲韻符號 = ('', '-', '+', '/調:')
    調符號 = ('/調:', '<', '>', '/詞:')
    詞符號 = ('/詞:', '!', '@', '/句:')
    句符號 = ('/句:', '^', '_', '')

    @classmethod
    def 生(cls, 輸出目的=open(os.devnull, 'w')):
        問題 = set()
        問題 |= cls.孤聲韻()
        print(len(問題), file=輸出目的)
        問題 |= cls.元音分韻()
        print(len(問題), file=輸出目的)
        問題 |= cls.孤元音()
        print(len(問題), file=輸出目的)
        問題 |= cls.陰聲韻()
        print(len(問題), file=輸出目的)
        問題 |= cls.鼻化韻佮聲化韻()
        print(len(問題), file=輸出目的)
        問題 |= cls.韻尾()
        print(len(問題), file=輸出目的)
        問題 |= cls.輔音()
        print(len(問題), file=輸出目的)
        問題 |= cls.指定調()
        print(len(問題), file=輸出目的)
        問題 |= cls.詞句長度(10, 20)
        print(len(問題), file=輸出目的)

        cls._生問題.檢查(問題)
        return 問題

    @classmethod
    def 孤聲韻(cls):
        聲韻 = []
        for 實際音 in itertools.chain(
                ['sil', 'sp'],
                臺灣閩南語羅馬字拼音對照音值聲母表.values(),
                臺灣閩南語羅馬字拼音對照音值韻母表.values()):
            聲韻.append(('{0}'.format(實際音), [實際音]))
        return cls._生問題.問題集(聲韻, cls.聲韻符號, '孤條')

    @classmethod
    def 元音分韻(cls):
        '''
                QS "Si7_Uan5_Im1"           {*-*a*+*,*-*i*+*,*-*u*+*,*-*e*+*,*-*o*+*}
                QS "Si7_Ting2_Uan5_Im1"      {*-*?i*+*,*-*?u*+*}
                QS "Si7_Tiong1_Uan5_Im1"    {*-*e*+*,*-*o*+*}
                QS "Si7_Ke1_Uan5_Im1"      {*-*a*+*}
        '''
        全部元音題目 = [('全部韻', ['*i*', '*ɨ*', '*u*', '*e*', '*ə*', '*o*', '*a*', ])]
        元音 = cls._生問題.問題集(全部元音題目, cls.聲韻符號, '孤條')
        懸低元音題目 = [
            ('懸元音韻', ['*i*', '*ɨ*', '*u*']),
            ('中元音韻', ['*e*', '*ə*', '*o*', ]),
            ('低元音韻', ['*a*', ])
        ]
        元音 |= cls._生問題.問題集(懸低元音題目, cls.聲韻符號, '孤條')
        前後元音題目 = [
            ('前元音韻', ['*i*', '*e*', ]),
            ('央元音韻', ['*ɨ*', '*ə*', '*a*', ]),
            ('後元音韻', ['*o*', '*u*'])
        ]
        元音 |= cls._生問題.問題集(前後元音題目, cls.聲韻符號, '孤條')
        孤元音題目 = [	]
        for 元音韻種類 in 全部元音題目[0][1]:
            孤元音題目.append(
                ('{}元音韻'.format(元音韻種類[1:-1]), [元音韻種類]))
        元音 |= cls._生問題.問題集(孤元音題目, cls.聲韻符號, '孤條')
        return 元音

    @classmethod
    def 孤元音(cls):
        '''
                QS "Si7_Sun5_Uan5_Im1"           {*-a+*,*-i+*,*-u+*,*-e+*,*-o+*}
        '''
        全部元音題目 = [('全部孤元音', ['i', 'ɨ', 'u', 'e', 'ə', 'o', 'a', ])]
        元音 = cls._生問題.問題集(全部元音題目, cls.聲韻符號, '孤條')
        懸低元音題目 = [
            ('懸孤元音', ['i', 'ɨ', 'u']),
            ('中孤元音', ['e', 'ə', 'o', ]),
            ('低孤元音', ['a', ])
        ]
        元音 |= cls._生問題.問題集(懸低元音題目, cls.聲韻符號, '孤條')
        前後元音題目 = [
            ('前孤元音', ['i', 'e', ]),
            ('央孤元音', ['ɨ', 'ə', 'a', ]),
            ('後孤元音', ['o', 'u'])
        ]
        元音 |= cls._生問題.問題集(前後元音題目, cls.聲韻符號, '孤條')
        孤元音題目 = [	]
        for 元音韻種類 in 全部元音題目[0][1]:
            孤元音題目.append(
                ('孤{}元音'.format(元音韻種類), [元音韻種類]))
        元音 |= cls._生問題.問題集(孤元音題目, cls.聲韻符號, '孤條')
        return 元音

    @classmethod
    def 陰聲韻(cls):
        '''
                QS "Si7_Sun5_Uan5_Im1"           {*-a+*,*-i+*,*-u+*,*-e+*,*-o+*}
        '''
        全部元音題目 = [('全部陰聲韻', ['*i', '*ɨ', '*u', '*e', '*ə', '*o', '*a', ])]
        陰聲韻 = cls._生問題.問題集(全部元音題目, cls.聲韻符號, '孤條')
        尾懸低元音題目 = [
            ('尾懸陰聲韻', ['*i', '*ɨ', '*u']),
            ('尾中陰聲韻', ['*e', '*ə', '*o', ]),
            ('尾低陰聲韻', ['*a', ])
        ]
        陰聲韻 |= cls._生問題.問題集(尾懸低元音題目, cls.聲韻符號, '孤條')
        尾前後元音題目 = [
            ('尾前陰聲韻', ['*i', '*e', ]),
            ('尾央陰聲韻', ['*ɨ', '*ə', '*a', ]),
            ('尾後陰聲韻', ['*o', '*u'])
        ]
        陰聲韻 |= cls._生問題.問題集(尾前後元音題目, cls.聲韻符號, '孤條')
        孤元音題目 = [	]
        for 元音韻種類 in 全部元音題目[0][1]:
            孤元音題目.append(
                ('尾{}陰聲韻'.format(元音韻種類[1:]), [元音韻種類]))
        陰聲韻 |= cls._生問題.問題集(孤元音題目, cls.聲韻符號, '孤條')

        頭懸低元音題目 = [
            ('頭懸陰聲韻', ['i*', 'ɨ*', 'u*']),
            ('頭中陰聲韻', ['e*', 'ə*', 'o*', ]),
            ('頭低陰聲韻', ['a*', ])
        ]
        陰聲韻 |= cls._生問題.問題集(頭懸低元音題目, cls.聲韻符號, '孤條')
        頭前後元音題目 = [
            ('頭前陰聲韻', ['i*', 'e*', ]),
            ('頭央陰聲韻', ['ɨ*', 'ə*', 'a*', ]),
            ('頭後陰聲韻', ['o*', 'u*'])
        ]
        陰聲韻 |= cls._生問題.問題集(頭前後元音題目, cls.聲韻符號, '孤條')
        孤元音題目 = [	]
        for 元音韻種類 in 全部元音題目[0][1]:
            孤元音題目.append(
                ('頭{}陰聲韻'.format(元音韻種類[1:]), [元音韻種類]))
        陰聲韻 |= cls._生問題.問題集(孤元音題目, cls.聲韻符號, '孤條')
        return 陰聲韻

    @classmethod
    def 鼻化韻佮聲化韻(cls):
        '''ⁿ
                QS "Si7_xm" {*-m̩+*}
                QS "Si7_xng" {*-ŋ̩+*}'''

        懸低鼻化音題目 = [
            ('懸鼻化韻', ['iⁿ', 'ɨⁿ', 'ŋ̩', ]),
            ('中鼻化韻', ['eⁿ', 'oⁿ', ]),
            ('低鼻化韻', ['m̩', 'aⁿ', ])
        ]
        前後鼻化音題目 = [
            ('唇鼻化韻', ['m̩', ]),
            ('前鼻化韻', ['iⁿ', 'eⁿ', ]),
            ('央鼻化韻', ['ɨⁿ', 'aⁿ', ]),
            ('後鼻化韻', ['oⁿ', 'ŋ̩', ])
        ]
        佇頭題目 = []
        佇尾題目 = []
        喉塞題目 = []
        for 原本題目 in [懸低鼻化音題目, 前後鼻化音題目]:
            for 名, 內容 in 原本題目:
                佇頭題目.append(('韻頭' + 名, list(map((lambda 內容: 內容 + '*'), 內容))))
                佇尾題目.append(('韻尾' + 名, list(map((lambda 內容: '*' + 內容), 內容))))
                喉塞題目.append(
                    ('喉塞' + 名, list(map((lambda 內容: '*' + 內容 + 'ʔ'), 內容))))
        鼻化韻 = set()
        for 改好題目 in [佇頭題目, 佇尾題目, 喉塞題目]:
            鼻化韻 |= cls._生問題.問題集(改好題目, cls.聲韻符號, '孤條')
        return 鼻化韻

    @classmethod
    def 韻尾(cls):
        韻尾題目 = [
            ('陽聲韻', ['*?m', '*?n', '*?ŋ']),
            ('入聲韻', ['*?p', '*?t', '*?k', '*?ʔ']),
        ]
        韻尾 = cls._生問題.問題集(韻尾題目, cls.聲韻符號, '孤條')
        孤韻 = []
        for 非陰聲 in 韻尾題目[0][1] + 韻尾題目[1][1]:
            孤韻.append(('是{}韻尾'.format(非陰聲[2:]), [非陰聲]))
        韻尾 |= cls._生問題.問題集(孤韻, cls.聲韻符號, '孤條')
        return 韻尾

    @classmethod
    def 輔音(cls):
        塞擦題目 = [
            ('塞音', ['p', 'pʰ', 'b', 't', 'tʰ', 'k', 'kʰ', 'g', 'ʔ', ]),
            ('塞擦音', ['ts', 'tsʰ', 'dz']),
            ('擦音', ['s', 'h', ]),
        ]
        發音方法 = [
            ('鼻音', ['m', 'n', 'ŋ']),
            ('清塞音', ['p', 't', 'k', 'ts', 'ʔ', ]),
            ('送氣音', ['pʰ', 'tʰ', 'kʰ', 'tsʰ', ]),
            ('濁塞音', ['b', 'g', 'dz', ]),
            ('濁輔音', ['b', 'g', 'dz', 'l']),
            ('濁非元音', ['m', 'n', 'ŋ', 'b', 'g', 'dz', 'l']),
        ]
        發音所在 = [
            ('唇輔音', ['p', 'pʰ', 'b', 'm']),
            ('齒輔音', ['t', 'tʰ', 'n', 'l', 'ts', 'tsʰ', 'dz', 's']),
            ('根輔音', ['k', 'kʰ', 'g', 'ŋ', ]),
            ('喉輔音', ['h', 'ʔ', ]),
        ]
        return cls._生問題.問題集(塞擦題目, cls.聲韻符號, '連紲') | \
            cls._生問題.問題集(發音方法, cls.聲韻符號, '孤條') | \
            cls._生問題.問題集(發音所在, cls.聲韻符號, '孤條')

    @classmethod
    def 聲韻前後(cls):
        '''
                QS "Si7_Ki2_Uan5_Im1"      {*-*i*+*,*-*e*+*,*-*a*+*}
                QS "Si7_Kin1_Uan5_Im1"    {*-*o*+*,*-*u*+*}
                QS "Si7_U7_Phinn5_Im1"    {*-*m*+*,*-*ng*+*}
                共i、佮n濫做伙，毋過可能無需要
        '''

    @classmethod
    def 指定調(cls):
        '''孤，孤條
        0:11
        1:33
        2:31
        3:11
        4:2
        5:12
        6:31
        7:22
        8:3
        9:23
        10:1
        '''
        孤調題目 = []
        for 調號 in range(0, 11):  # 有輕聲到第十調
            孤調題目.append(('第{}調'.format(調號), ['{}'.format(調號)]))
        return cls._生問題.問題集(孤調題目, cls.調符號, '孤條')


if __name__ == '__main__':
    問題 = 閩南語決策樹仔().生(sys.stdout)
    檔案 = open('questions_qst001.hed', 'w')
    print('\n'.join(問題), file=檔案)
    檔案.close()
