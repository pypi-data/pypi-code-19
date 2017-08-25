import re


class 提出通用音標:

    @classmethod
    def 揣音標(cls, trs聽拍):
        trs聽拍 = trs聽拍.strip()
        trs聽拍 = re.sub(r'\[//\]', '-X-', trs聽拍)
        trs聽拍 = re.sub(r'\[[^\]]*\]', '', trs聽拍)
        trs聽拍 = re.sub(r'\([^\)]*\)', '', trs聽拍)
        if trs聽拍.endswith('//'):
            答案 = re.sub(r'[^a-z0-9/]*//', ' ', trs聽拍).strip()
        elif '/' in trs聽拍:
            答案 = re.sub(r'.*/', '', trs聽拍)
        else:
            答案 = re.sub(r'.*[^a-zA-Z0-9\- _,]', '', trs聽拍)
        return 答案.strip()
