#!/usr/bin/env python3
# 项目：自用函数库
# 模块：校验位计算模块
# 作者：黄涛

def checksum(s,calc,Key,Sum):
    return Sum[sum([calc(c,k) for c,k in zip(s,Key)])%len(Sum)]

def circle(s):
    while True:
        for i in s:
            yield i
    
def id_card(card_no):
    '''修正居民身份证的校验位'''
    Key=(7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2)
    Sum='10X98765432'
    length=len(card_no)
    if 15==length:
        card_no='19'.join([card_no[:6],card_no[6:]])
        length+=2
    if 18>=length>=17:
        return card_no[:17]+checksum(card_no[:17],\
                        lambda x,y:int(x)*y,Key,Sum)

def org_code(code_no):
    '''修正组织机构代码证校验位'''
    key=(3,7,9,10,5,8,4,2)
    Sum='0X987654321'
    code_no=code_no[:8].upper()
    def calc(c,k):
        if '0'<=c<='9':
            return int(c)*k
        elif 'A'<=c<='Z':
            return (ord(c)-0X37)*k
        else:
            return 0
    return '-'.join([code_no,checksum(code_no,calc,key,Sum)])
    
def bank_card(card_no):
    '''修正银行卡校验位'''
    Sum='0987654321'
    if len(card_no) in (16,17,19):
        card_no=card_no[:-1]
        return card_no+checksum(reversed(card_no),
                        lambda x,y:sum(divmod(int(x)*y,10)),
                        circle([2,1]),Sum)

def czbank_ac(acno):
    '''账号校验位算法'''
    keys=30,3,50,5,70,7,10,11,30,13,70,17,90,19,30,23,90,29,10,31
    if len(acno)>=20:
        checksum='%02d'%(sum([int(x)*k for x,k in zip(acno,keys)]))
        if acno[11]=='9':
            return '%s%s'%(acno[:21],checksum[-2])
        else:
            return '%s%s'%(acno[:20],checksum[-2:])

def credit_code(code):
    Base="0123456789ABCDEFGHJKLMNPQRTUWXY"
    wi=1, 3, 9, 27, 19, 26, 16, 17, 20, 29, 25, 13, 8, 24, 10, 30, 28
    if len(code)>=17:
        check=sum([Base.index(k)*w for k,w in zip(code,wi)])%31
        if check:
            check=31-check
        return '%s%s'%(code[:17],Base[check])
        
    
if __name__=='__main__':
    print(id_card('310115201411142227'))
    print(id_card('412902197909022053'))
    print(bank_card('3568680095415995'))
    print(bank_card('6223093310810005226'))
    print(org_code('L2345678-1'))
    print(org_code('74371976-1'))
    print(credit_code('91460600MA5RC30P9Y'))
        
