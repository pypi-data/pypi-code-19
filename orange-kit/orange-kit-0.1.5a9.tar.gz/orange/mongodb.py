# 项目：标准库函数
# 模块：配置mongodb数据库
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2016-11-19 10:18

import sys
from orange.deploy import *
from orange import exec_shell,read_shell

SERVERNAME='MongoDb'
def win_deploy():
    root=get_path(SERVERNAME,False)[0]
    data=root / 'data'
    data.ensure()
    result=read_shell('sc query %s'%(SERVERNAME))
    if 'SERVICE_NAME:' in result[1]:    # 检查服务是否安装
        print('%s 服务已安装！'%(SERVERNAME))
        if 'STOPPED' in result[3]:
            exec_shell('sc start %s'%(SERVERNAME))
        return
    
    cmd=('mongod','--install',     # 作为服务安装
         '--serviceName %s'%(SERVERNAME),  # 服务名称
      '--logpath %s\\mongodb.log'%(root),   # 日志文件
      '--logappend',                        # 日志采用添加模式
      '--dbpath %s'%(data),                 # 数据文件目录
      '--directoryperdb',                   # 每个数据库采用单一文件
      )
    r=exec_shell(' '.join(cmd))
    exec_shell('sc start %s'%(SERVERNAME))
    if r==0:
        print('%s 服务安装成功！'%(SERVERNAME))

def darwin_deploy():
    pass
    
def main():
    import sys
    if sys.platform=='win32':
        win_deploy()
    elif sys.platform=='darwin':
        darwin_deploy()
    else:
        print('操作系统%下的配置未实现')

if __name__=='__main__':
    main()
