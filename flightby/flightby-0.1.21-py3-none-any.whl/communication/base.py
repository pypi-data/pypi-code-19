import abc 
from enum import Enum



class ISerializable:
    
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def getSize(self):
        pass

    @abc.abstractmethod
    def ToArray(self):
        pass



# 데이터 수신 상태
class StateLoading(Enum):
    
    Ready           = 0x00      # 수신 대기
    Receiving       = 0x01      # 수신중
    Loaded          = 0x02      # 수신 완료 후 명령어 보관소에 대기중
    Failure         = 0x03      # 수신 실패



# 데이터 섹션 구분
class Section(Enum):

    Start           = 0x00      # 전송 시작 코드
    Header          = 0x01      # 헤더
    Data            = 0x02      # 데이터
    End             = 0x03      # 데이터 확인
    

