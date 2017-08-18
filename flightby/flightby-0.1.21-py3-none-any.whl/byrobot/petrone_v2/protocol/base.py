import numpy as np
from struct import *
from enum import Enum
import os

from flightby.byrobot.petrone_v2.protocol.system import *
from flightby.communication.base import ISerializable



class DataType(Enum):
    
    None_               = 0x00      # 없음
    
    Ping                = 0x01      # 통신 확인
    Ack                 = 0x02      # 데이터 수신에 대한 응답
    Error               = 0x03      # 오류(reserve 비트 플래그는 추후에 지정)
    Request             = 0x04      # 지정한 타입의 데이터 요청
    Message             = 0x05      # 문자열 데이터
    Reserved_1          = 0x06      # 예약
    Reserved_2          = 0x07      # 예약
    Monitor             = 0x08      # 디버깅용 값 배열 전송. 첫번째 바이트에 타입 두 번째 바이트에 페이지 지정(수신 받는 데이터의 저장 경로 구분)
    SystemCounter       = 0x09      # 시스템 카운터
    Information         = 0x0A      # 장치 정보
    UpdateLocation      = 0x0B      # 펌웨어 업데이트 위치 정정
    Update              = 0x0C      # 펌웨어 업데이트
    Encrypt             = 0x0D      # 펌웨어 암호화
    Address             = 0x0E      # 장치 주소
    Administrator       = 0x0F      # 관리자 권한 획득
    Control             = 0x10      # 조종 명령

    Command             = 0x11      # 명령

    # Light
    LightManual                 = 0x20      # LED 수동 제어

    LightMode                   = 0x21      # LED 모드 지정
    LightModeCommand            = 0x22      # LED 모드 커맨드
    LightModeCommandIr          = 0x23      # LED 모드 커맨드 IR 데이터 송신
    LightModeColor              = 0x24      # LED 모드 3색 직접 지정
    LightModeColorCommand       = 0x25      # LED 모드 3색 직접 지정 커맨드
    LightModeColorCommandIr     = 0x26      # LED 모드 3색 직접 지정 커맨드 IR 데이터 송신
    LightModeColors             = 0x27      # LED 모드 팔레트의 색상으로 지정
    LightModeColorsCommand      = 0x28      # LED 모드 팔레트의 색상으로 지정 커맨드
    LightModeColorsCommandIr    = 0x29      # LED 모드 팔레트의 색상으로 지정 커맨드 IR 데이터 송신

    LightEvent                  = 0x2A      # LED 이벤트
    LightEventCommand           = 0x2B      # LED 이벤트 커맨드
    LightEventCommandIr         = 0x2C      # LED 이벤트 커맨드 IR 데이터 송신
    LightEventColor             = 0x2D      # LED 이벤트 3색 직접 지정
    LightEventColorCommand      = 0x2E      # LED 이벤트 3색 직접 지정 커맨드
    LightEventColorCommandIr    = 0x2F      # LED 이벤트 3색 직접 지정 커맨드 IR 데이터 송신
    LightEventColors            = 0x30      # LED 이벤트 팔레트의 색상으로 지정
    LightEventColorsCommand     = 0x31      # LED 이벤트 팔레트의 색상으로 지정 커맨드
    LightEventColorsCommandIr   = 0x32      # LED 이벤트 팔레트의 색상으로 지정 커맨드 IR 데이터 송신

    LightModeDefaultColor       = 0x33      # LED 초기 모드 3색 직접 지정

    # 상태 설정
    State           = 0x40      # 드론의 상태(비행 모드 방위기준 배터리량)
    Attitude        = 0x41      # 드론의 자세(Angle)(Vector)
    GyroBias        = 0x42      # 자이로 바이어스 값(Vector)
    TrimAll         = 0x43      # 전체 트림
    TrimFlight      = 0x44      # 비행 트림
    TrimDrive       = 0x45      # 주행 트림

    # Sensor raw data
    Imu             = 0x50      # IMU Raw
    Pressure        = 0x51      # 압력 센서 데이터
    Battery         = 0x52      # 배터리
    Range           = 0x53      # 적외선 거리 센서
    ImageFlow       = 0x54      # ImageFlow
    CameraImage     = 0x55      # CameraImage

    # Input
    Button          = 0x70      # 버튼 입력
    Joystick        = 0x71      # 조이스틱 입력

    # Devices
    Motor           = 0x80      # 모터 제어 및 현재 제어값 확인
    MotorSingle     = 0x81      # 한 개의 모터 제어
    IrMessage       = 0x82      # IR 데이터 송수신
    Buzzer          = 0x83      # 부저 제어
    Vibrator        = 0x84      # 진동 제어

    # 카운트
    CountFlight     = 0x90      # 비행 관련 카운트
    CountDrive      = 0x91      # 주행 관련 카운트

    # RF
    Pairing         = 0xA0      # 페어링
    Rssi            = 0xA1      # RSSI

    # Display
    DisplayClear            = 0xB0      # 화면 지우기
    DisplayInvert           = 0xB1      # 화면 반전
    DisplayDrawPoint        = 0xB2      # 점 그리기
    DisplayDrawLine         = 0xB3      # 선 그리기
    DisplayDrawRect         = 0xB4      # 사각형 그리기
    DisplayDrawCircle       = 0xB5      # 원 그리기
    DisplayDrawString       = 0xB6      # 문자열 쓰기
    DisplayDrawStringAlign  = 0xB7      # 문자열 쓰기

    EndOfType               = 0xB8



class CommandType(Enum):
    
    None_               = 0x00      # 없음

    # 설정
    ModeVehicle         = 0x10      # Vehicle 동작 모드 전환

    # 제어
    Coordinate          = 0x20      # 방위 기준 변경
    Trim                = 0x21      # 트림 변경
    FlightEvent         = 0x22      # 비행 이벤트 실행
    DriveEvent          = 0x23      # 주행 이벤트 실행
    Stop                = 0x24      # 정지

    ClearTrim           = 0x50      # 트림 초기화
    ClearGyroBias       = 0x51      # 자이로 바이어스 리셋(트림도 같이 초기화 됨)

    DataStorageWrite    = 0x80      # 변경사항이 있는 경우 데이터 저장소에 기록

    # 관리자
    ClearCounter        = 0xA0      # 카운터 클리어(관리자 권한을 획득했을 경우에만 동작)
    SetTestComplete     = 0xA1      # 테스트 완료 처리

    EndOfType           = 0xA2



class Header(ISerializable):

    def __init__(self):
        
        self.dataType    = DataType.None_
        self.length      = 0
        self.from_       = DeviceType.None_
        self.to_         = DeviceType.None_


    @classmethod
    def getSize(cls):
        return 4


    def toArray(self):
        return pack('<BBBB', self.dataType.value, self.length, self.from_.value, self.to_.value)


    @classmethod
    def parse(cls, dataArray):
        header = Header()

        if len(dataArray) != cls.getSize():
            #print("{0}".format(dataArray.count))
            return None

        header.dataType, header.length, header.from_, header.to_ = unpack('<BBBB', dataArray)

        header.dataType = DataType(header.dataType)
        header.from_ = DeviceType(header.from_)
        header.to_ = DeviceType(header.to_)
        
        return header


