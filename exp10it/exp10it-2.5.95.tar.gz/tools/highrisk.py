from exp10it import ModulePath
def single_risk_scan(target):
    # 单个target高危exp遍历模块
    # target要求为http(s)+domain格式
    # risk_scan模块对每个target,无论是主要目标的旁站还是子站,都进行详细的判断target是否是主要目标,并在对应的表
    # 中记录risk_scaned的完成状态
    # 这里的target不一定是主要目标,可以是旁站或子站
    import os
    # url属于哪个主目标(非旁站子站的那个目标)
    # 如http://wit.freebuf.com得到www.freebuf.com
    # eg.www_freebuf_com_pang


    exp_list = os.listdir(ModulePath + "exps")
    for each in exp_list:
        command = "cd %s/%s && python3 %s.py %s" % (ModulePath + "exps", each, each, target)
        os.system(command)
        if os.path.exists(ModulePath + "exps/%s/result.txt" % each):
            with open(ModulePath + "exps/%s/result.txt", "r+") as f:
                strings_to_write = f.read()
        else:
            strings_to_write = ""
    return strings_to_write

if __name__=="__main__":
    import sys
    single_risk_scan(sys.argv[1])
