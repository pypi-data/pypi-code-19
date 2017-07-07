# -*- coding: utf-8 -*-
from pybythec import utils
from pybythec.BuildStatus import BuildStatus
from pybythec.BuildElements import BuildElements

import os
import sys
import time
from threading import Thread

import logging
logging.basicConfig(level = logging.INFO, format = '%(levelname)s: %(name)s: %(message)s')
log = logging.getLogger('pybythec')

__author__ = 'glowtree'
__email__ = 'tom@glowtree.com'
__version__ = '0.9.26'


def build(version = None,
          compiler = None,
          osType = None,
          buildType = None,
          binaryFormat = None,
          projConfigPath = None,
          globalConfigPath = None,
          builds = None,
          projConfig = None,
          globalConfig = None,
          libDir = None):
  '''
    version: just log the current version number
    compiler: any variation of gcc, clang, or msvc ie g++-4.4, msvc110
    osType: operating system: currently linux, macOs, or windows
    buildType: debug release etc
    binaryFormat: 32bit, 64bit etc
    projConfigPath: path to a pybythec project config file (json)
    globalConfigPath: path to a pybythec global config file (json)
    builds: list of build variations
    projConfig: dict of the project config
    globalConfig: dict of the global config
    libDir: directory path of the library being built, likely only used when building a library as a dependency (ie from a project)
  '''

  if version:
    log.info('version: ' + __version__)
    return 0

  be = BuildElements(
      osType = osType,
      projConfig = projConfig,
      projConfigPath = projConfigPath,
      builds = builds,
      globalConfig = globalConfig,
      globalConfigPath = globalConfigPath,
      libDir = libDir)

  # iterate through the builds
  for buildName in be.builds:
    be.configBuild(compiler = compiler, buildType = buildType, binaryFormat = binaryFormat, buildName = buildName)
    _build(be)


def _build(be):
  '''
  '''
  buildStatus = BuildStatus(be.target, be.buildPath)

  # lock - early return
  if be.locked and os.path.exists(be.targetInstallPath):
    buildStatus.writeInfo('locked', be.target + ' is locked')
    return True

  startTime = time.time()

  threading = True

  log.info('building ' + be.infoStr)

  buildingLib = False
  if be.libDir:
    buildingLib = True

  if not os.path.exists(be.installPath):
    utils.createDirs(be.installPath)

  if not os.path.exists(be.buildPath):
    os.makedirs(be.buildPath)

  incPathList = []
  for incPath in be.incPaths:
    if os.path.exists(incPath):
      incPathList += ['-I', incPath]
    else:
      log.warning('incPath {0} doesn\'t exist'.format(incPath))

  for extIncPath in be.extIncPaths:  # external include libs (for cases where 3rd party header includes are using "" instead of <> ie Unreal)
    if os.path.exists(incPath):
      incPathList += ['-I', extIncPath]
    else:
      log.warning('extIncPath {0} doesn\'t exist'.format(extIncPath))

  definesList = []
  for define in be.defines:
    definesList += ['-D', define]

  #
  # qt moc file compilation
  #
  mocPaths = []
  for qtClass in be.qtClasses:
    found = False
    mocPath = '{0}/moc_{1}.cpp'.format(be.buildPath, qtClass)
    qtClassHeader = qtClass + '.h'

    for incPath in be.incPaths:  # find the header file, # TODO: should there be a separate list of headers ie be.mocIncPaths?
      includePath = incPath + '/' + qtClassHeader
      if not os.path.exists(includePath):
        continue

      if os.path.exists(mocPath) and float(os.stat(mocPath).st_mtime) < float(os.stat(includePath).st_mtime) or not os.path.exists(mocPath):
        buildStatus.description = 'qt moc: ' + utils.runCmd(['moc'] + definesList + [includePath, '-o', mocPath])

      if not os.path.exists(mocPath):
        buildStatus.writeError(buildStatus.description)
        return False

      mocPaths.append(mocPath)
      found = True

    if not found:
      buildStatus.writeError('can\'t find {0} for qt moc compilation'.format(qtClassHeader))
      return False

  for mocPath in mocPaths:
    be.sources.append(mocPath)

  buildStatusDeps = []  # the build status for each dependency: objs and libs
  threads = []
  i = 0

  #
  # compile
  #
  objPaths = []
  cmd = [be.compilerCmd, be.objFlag] + incPathList + definesList + be.flags

  if threading:
    for source in be.sources:
      buildStatusDep = BuildStatus(source)
      buildStatusDeps.append(buildStatusDep)
      thread = Thread(None, target = _compileSrc, args = (be, cmd, source, objPaths, buildStatusDep))
      thread.start()
      threads.append(thread)
      i += 1
  else:
    for source in be.sources:
      buildStatusDep = BuildStatus(source)
      buildStatusDeps.append(buildStatusDep)
      _compileSrc(be, cmd, source, objPaths, buildStatusDep)
      i += 1

  #
  # build library dependencies
  #
  libCmds = []
  libsBuilding = []
  if be.binaryType == 'exe' or be.binaryType == 'plugin':
    for lib in be.libs:
      libName = lib
      if be.compiler.startswith('msvc'):
        libCmds += [libName + be.staticExt]  # you need to link against the .lib stub file even if it's ultimately a .dll that gets linked
      else:
        libCmds += [be.libFlag, libName]

      # check if the lib has a directory for building
      if threading:
        for libSrcDir in be.libSrcPaths:
          libSrcDir = os.path.join(libSrcDir, lib)
          if os.path.exists(libSrcDir):
            libsBuilding.append(lib)
            buildStatusDep = BuildStatus(lib)
            buildStatusDeps.append(buildStatusDep)
            thread = Thread(None, target = _buildLib, args = (be, libSrcDir, buildStatusDep))
            thread.start()
            threads.append(thread)
            i += 1
            break
      else:
        for libSrcPath in be.libSrcPaths:
          if not os.path.exists('libSrcPath'):
            log.warning('libSrcPath {0} doesn\'t exist'.format(libSrcPath))
            continue
          libSrcPath = os.path.join(libSrcPath, lib)
          if os.path.exists(libSrcPath):
            libsBuilding.append(lib)
            buildStatusDep = BuildStatus(lib)
            buildStatusDeps.append(buildStatusDep)
            _buildLib(be, libSrcDir, buildStatusDep)
            i += 1
            break

  # wait for all the threads before checking the results
  for thread in threads:
    thread.join()

  allUpToDate = True
  for buildStatusDep in buildStatusDeps:
    if buildStatusDep.status == 'failed':
      buildStatus.writeError('{0} failed because {1} failed because...\n\n{2}\n...determined in seconds\n\n'.format(
          be.infoStr, buildStatusDep.name, buildStatusDep.description.encode('ascii', 'ignore'), str(int(time.time() - startTime))))
      return False
    elif buildStatusDep.status == 'built':
      allUpToDate = False

  # revise the library paths
  for i in range(len(be.libPaths)):
    revisedLibPath = be.libPaths[i] + be.binaryRelPath
    if os.path.exists(revisedLibPath):
      be.libPaths[i] = revisedLibPath

  #
  # linking
  #
  linkCmd = []

  if allUpToDate and os.path.exists(be.targetInstallPath):
    buildStatus.writeInfo('up to date', '{0} is up to date, determined in {1} seconds\n'.format(be.infoStr, str(int(time.time() - startTime))))
    if not buildingLib:
      _runPostScript(be)
    return True

  # microsoft's compiler / linker can only handle so many characters on the command line
  msvcLinkCmdFilePath = be.buildPath + '/linkCmd'
  if be.compiler.startswith('msvc'):
    msvcLinkCmd = '{0}"{1}" "{2}" {3}'.format(be.targetFlag, be.targetInstallPath, '" "'.join(objPaths), ' '.join(libCmds))
    msvcLinkCmdFp = open(msvcLinkCmdFilePath, 'w')
    msvcLinkCmdFp.write(msvcLinkCmd)
    msvcLinkCmdFp.close()
    linkCmd += [be.linker, '@' + msvcLinkCmdFilePath]
    if be.showLinkerCmds:
      log.info('\nmsvcLinkCmd: {0}\n'.format(msvcLinkCmd))
  else:
    linkCmd += [be.linker, be.targetFlag, be.targetInstallPath] + objPaths + libCmds

  if be.binaryType != 'static':  # TODO: is this the case for msvc?
    linkCmd += be.linkFlags

  if be.binaryType == 'exe' or be.binaryType == 'plugin' or (be.compilerRoot == 'msvc' and be.binaryType == 'dynamic'):

    for libPath in be.libPaths:
      if not os.path.exists(libPath):
        log.warning('libPath {0} doesn\'t exist'.format(libPath))
        continue
      if be.compiler.startswith('msvc'):
        linkCmd += [be.libPathFlag + os.path.normpath(libPath)]
      else:
        linkCmd += [be.libPathFlag, os.path.normpath(libPath)]

  # get the timestamp of the existing target if it exists
  linked = False
  targetExisted = False
  oldTargetTimeStamp = None
  if os.path.exists(be.targetInstallPath):
    oldTargetTimeStamp = float(os.stat(be.targetInstallPath).st_mtime)
    targetExisted = True

  if be.showLinkerCmds:
    log.info('\n{0}\n'.format(' '.join(linkCmd)))

  buildStatus.description = utils.runCmd(linkCmd)

  if os.path.exists(be.targetInstallPath):
    if targetExisted:
      if float(os.stat(be.targetInstallPath).st_mtime) > oldTargetTimeStamp:
        linked = True
    else:
      linked = True

  if linked:
    log.info('linked ' + be.infoStr)
  else:
    buildStatus.writeError('linking failed because ' + buildStatus.description)
    return False

  # copy dynamic library dependencies (built by this build) to the install path   
  if be.binaryType == 'exe' or be.binaryType == 'plugin':
    for lib in libsBuilding:
      for libPath in be.libPaths:
        dynamicPath = libPath + '/'
        if be.compilerRoot == 'gcc' or be.compilerRoot == 'clang':
          dynamicPath += 'lib'
        dynamicPath += lib + be.dynamicExt
        if os.path.exists(dynamicPath):
          utils.copyfile(dynamicPath, be.installPath)

  buildStatus.writeInfo('built', '{0} built {1}\ncompleted in {2} seconds\n'.format(be.infoStr, be.targetInstallPath,
                                                                                    str(int(time.time() - startTime))))

  sys.stdout.flush()

  # run a post-build script if it exists
  if not buildingLib:
    _runPostScript(be)

  return True


#
# private functions
#
def _compileSrc(be, compileCmd, source, objPaths, buildStatus):
  '''
    be (in): BuildElements object
    compileCmd (in): the compile command so far 
    source (in): the c or cpp source file to compile (every source file gets it's own object file)
    objPaths (out): list of all object paths that will be passed to the linker
    buildStatus (out): build status for this particular compile
  '''

  if not os.path.exists(source):
    buildStatus.writeError(source + ' is missing, exiting build')
    return

  objFile = os.path.basename(source)
  objFile = objFile.replace(os.path.splitext(source)[1], be.objExt)
  objPath = os.path.join(be.buildPath, objFile)
  objPaths.append(objPath)

  # check if it's up to date
  objExisted = os.path.exists(objPath)
  if objExisted:
    objTimestamp = float(os.stat(objPath).st_mtime)
    if not utils.sourceNeedsBuilding(be.incPaths, source, objTimestamp):
      buildStatus.status = 'up to date'
      return

  # Microsoft Visual C has to have the objPathFlag cuddled up directly next to the objPath - no space in between them (grrr)
  if be.compiler.startswith('msvc'):
    cmd = compileCmd + [source, be.objPathFlag + objPath]
  else:
    cmd = compileCmd + [source, be.objPathFlag, objPath]

  if be.showCompilerCmds:
    log.info('\n' + ' '.join(cmd) + '\n')

  buildStatus.description = utils.runCmd(cmd)

  if os.path.exists(objPath):
    if objExisted:
      if float(os.stat(objPath).st_mtime) > objTimestamp:
        buildStatus.status = 'built'
    else:
      buildStatus.status = 'built'

  if buildStatus.status == 'built':
    buildStatus.description = 'compiled ' + os.path.basename(source)


def _buildLib(be, libSrcDir, buildStatus):
  '''
  '''
  jsonPath = os.path.join(libSrcDir, 'pybythec.json')
  if not os.path.exists(jsonPath):
    jsonPath = os.path.join(libSrcDir, '.pybythec.json')
  if not os.path.exists(jsonPath):
    buildStatus.writeError(libSrcDir + ' does not have a pybythec.json file')
    return

  build(
      osType = be.osType,
      compiler = be.compiler,
      buildType = be.buildType,
      binaryFormat = be.binaryFormat,
      projConfig = be.projConfig,
      globalConfig = be.globalConfig,
      libDir = libSrcDir)

  # read the build status
  buildStatus.readFromFile(libSrcDir, be.buildDir, be.buildType, be.compiler, be.binaryFormat)


def clean(osType = None,
          compiler = None,
          buildType = None,
          binaryFormat = None,
          projConfigPath = None,
          globalConfigPath = None,
          builds = None,
          projConfig = None,
          globalConfig = None,
          libDir = None):
  '''
  '''
  be = BuildElements(
      osType = osType,
      projConfigPath = projConfigPath,
      globalConfigPath = globalConfigPath,
      builds = builds,
      projConfig = projConfig,
      globalConfig = globalConfig,
      libDir = libDir)
  for buildName in be.builds:
    be.configBuild(compiler = compiler, buildType = buildType, binaryFormat = binaryFormat, buildName = buildName)
    _clean(be)


def _clean(be):
  '''
    cleans the current project
    be (in): BuildElements object
  '''
  # remove any dynamic libs that are sitting next to the exe
  if os.path.exists(be.installPath) and (be.binaryType == 'exe' or be.binaryType == 'plugin'):
    for f in os.listdir(be.installPath):
      libName, ext = os.path.splitext(f)
      if ext == be.dynamicExt:
        if be.compilerRoot == 'gcc' or be.compilerRoot == 'clang':
          libName = libName.lstrip('lib')
        for lib in be.libs:
          if lib == libName:
            p = be.installPath + '/' + f
            try:
              os.remove(p)
            except:
              log.warning('failed to remove ' + p)
      elif ext == '.exp' or ext == '.ilk' or ext == '.lib' or ext == '.pdb':  # msvc files
        p = be.installPath + '/' + f
        try:
          os.remove(p)
        except:
          log.warning('failed to remove ' + p)

  if not os.path.exists(be.buildPath):  # canary in the coal mine
    log.info(be.infoStr + ' already clean')
    return True

  dirCleared = True
  for f in os.listdir(be.buildPath):
    p = be.buildPath + '/' + f
    try:
      os.remove(p)
    except:
      dirCleared = False
      log.warning('failed to remove {0}'.format(p))
  if dirCleared:
    os.removedirs(be.buildPath)

  if os.path.exists(be.targetInstallPath):
    os.remove(be.targetInstallPath)
  target, ext = os.path.splitext(be.targetInstallPath)
  if ext == '.dll':
    try:
      os.remove(target + '.exp')
      os.remove(target + '.lib')
    except:
      pass
  try:
    os.removedirs(be.installPath)
  except:
    pass

  log.info(be.infoStr + ' all clean')
  return True


def cleanAll(osType = None, compiler = None, buildType = None, binaryFormat = None, projConfigPath = None, globalConfigPath = None, builds = None):
  '''
    cleans both the current project and also the dependencies
  '''
  be = BuildElements(osType = osType, projConfigPath = projConfigPath, globalConfigPath = globalConfigPath, builds = builds)
  for buildName in be.builds:
    be.configBuild(compiler = compiler, buildType = buildType, binaryFormat = binaryFormat, buildName = buildName)
    _clean(be)

    # clean library dependencies
    for lib in be.libs:
      for libSrcPath in be.libSrcPaths:
        libPath = os.path.join(libSrcPath, lib)
        if os.path.exists(libPath):
          clean(
              osType = be.osType,
              compiler = be.compiler,
              buildType = be.buildType,
              binaryFormat = be.binaryFormat,
              projConfig = be.projConfig,
              globalConfig = be.globalConfig,
              libDir = libPath)


def _runPostScript(be):
  '''
    looks for a post-build script and loads it as a module
  '''
  postScriptPath = './pybythecPost.py'
  if not os.path.exists(postScriptPath):
    postScriptPath = './.pybythecPost.py'
  if os.path.exists(postScriptPath):
    import imp
    m = imp.load_source('', postScriptPath)
    m.run(be)
