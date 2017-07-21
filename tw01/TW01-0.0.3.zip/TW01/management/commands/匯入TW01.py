from os import walk
from subprocess import PIPE
import subprocess

from django.core.management import call_command
from django.core.management.base import BaseCommand


from 臺灣言語資料庫.資料模型 import 來源表
from 臺灣言語資料庫.資料模型 import 影音表
from 臺灣言語資料庫.資料模型 import 版權表
from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from 臺灣言語工具.解析整理.解析錯誤 import 解析錯誤
from 臺灣言語工具.音標系統.閩南語.通用拼音音標 import 通用拼音音標
from os.path import join, basename


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '語料目錄',
            type=str,
        )
        parser.add_argument(
            '--匯入幾筆',
            type=int,
            default=100000,
            help='試驗用，免一擺全匯'
        )

    def handle(self, *args, **參數):
        call_command('顯示資料數量')

        音檔資料 = []
        for 所在, _資料夾陣列, 檔案陣列 in sorted(walk(參數['語料目錄'])):
            for 檔案 in 檔案陣列:
                路徑 = join(所在, 檔案)
                if 路徑.endswith('.tcp'):
                    proc = subprocess.Popen(
                        ['iconv', '-f', 'big5', '-t', 'utf8', 路徑], stdout=PIPE
                    )
                    outs, _errs = proc.communicate()
#                     print(路徑)
                    for 一逝 in outs.decode().split('\n'):
                        if 一逝.strip():
                            編號, 漢羅, 通用 = 一逝.split()
                            音檔路徑 = join(所在, 編號 + '.wav')
#                             資料[編號] = (漢字, 通用)
                            try:
                                正規化物件 = (
                                    拆文分析器
                                    .對齊組物件(漢羅, 通用.replace('_', ' '))
                                    .轉音(通用拼音音標)
                                )
                                音檔資料.append(
                                    (basename(所在), 音檔路徑, 正規化物件)
                                )
                            except 解析錯誤:
                                print(漢羅, 通用)
                                pass
        公家內容 = {
            '收錄者': 來源表.objects.get_or_create(名='系統管理員')[0].編號(),
            '來源': 來源表.objects.get_or_create(名='TW01')[0].編號(),
            '版權': 版權表.objects.get_or_create(版權='毋知')[0].pk,
            '種類': '字詞',
            '語言腔口': '臺語',
            '著作所在地': '臺灣',
            '著作年': '2000',
        }
        匯入數量 = 0
        for 語者, 音檔路徑, 正規化物件 in 音檔資料:
            影音內容 = {
                '影音所在': 音檔路徑,
                '屬性': {'語者': 語者},
            }
            影音內容.update(公家內容)
            影音 = 影音表.加資料(影音內容)
            文本內容 = {
                '文本資料': 正規化物件.看型(),
                '音標資料': 正規化物件.看音(),
            }
            文本內容.update(公家內容)
            影音.寫文本(文本內容)
            聽拍內容 = {'聽拍資料': [{
                '開始時間': 0,
                '結束時間': 影音.聲音檔().時間長度(),
                '內容': 正規化物件.看分詞(),
                '語者': 語者,
            }]}
            聽拍內容.update(公家內容)
            影音.寫聽拍(聽拍內容)

            匯入數量 += 1
            if 匯入數量 % 100 == 0:
                print('匯入 {} 筆'.format(匯入數量))
            if 匯入數量 == 參數['匯入幾筆']:
                break

        call_command('顯示資料數量')
