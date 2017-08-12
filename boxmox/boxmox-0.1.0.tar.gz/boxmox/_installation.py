import os
import sys
if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as s
else:
    import subprocess as s

def validate():

    # 1) BOXMOX is installed and working
    if 'KPP_HOME' in os.environ.keys():
        try:
            res = s.check_call("validate_BOXMOX_installation")
        except:
            print("BOXMOX installation broken!")
            return None
    else:
        print('$KPP_HOME not found in environment - is BOXMOX installed?')
        return None

    # 2) an work directory has been defined and is useable
    if 'BOXMOX_WORK_PATH' in os.environ.keys():
        work_path = os.environ['BOXMOX_WORK_PATH']
        try:
            if not os.path.isdir(work_path):
                os.makedirs(work_path)
        except:
            print("Could not create work directory " + work_path)
            return None
    else:
        print('BOXMOX_WORK_PATH not found in environment - set it to a path were BOXMOX can write stuff to.')
        return None

    return work_path
