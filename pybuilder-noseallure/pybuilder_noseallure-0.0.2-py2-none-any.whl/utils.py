import os

def getImportantDirs(project):
    cwd = os.getcwd()
    log_dir = cwd + "/" + project.expand("$dir_target/allure_report_logs")
    test_dir = cwd + "/" + project.get_property("dir_source_unittest_python", 'src/unittest/python')
    return (test_dir, log_dir)

def prepareArgs(project):
    args = []

    for propName in project.properties:
        propValue = project.properties[propName]
        if propName.startswith('nose_'):
            propName = propName.replace('nose_', '')
        
            if isinstance(propValue, (type(None), str, int, float, bool)) or not hasattr(propValue, '__iter__'):
                propValue = [propValue]
            
            for pv in propValue:
                if pv == True:
                    args.append('--' + str(propName))
                elif pv != False and pv != None and propName != "dir_dist_scripts" and propName != "distutils_readme_file":
                    args.append('--' + propName + '=' + str(pv))
    
    return args

  
