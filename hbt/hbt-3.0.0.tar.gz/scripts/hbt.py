#! /usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (C) 2017 贵阳货车帮科技有限公司
#

import re
import os
import sys
import subprocess
import platform
import time
from jira import JIRA

# checkstyle problem level
LEVEL_ERROR = 'ERROR'
LEVEL_WARN = 'WARN'

CHECKSTYLE_JAR_FILE_NAME = 'checkstyle-all.jar'
CHECKSTYLE_CONFIG_FILE_NAME = 'checkstyle-config.xml'

JAVA_FILE_SUFFIX = '.java'
XML_FILE_SUFFIX = '.xml'

# example: "M  src/main/java/com/wlqq/checkout/CheckOutActivity.java"
# example: "A  src/main/res/values/strings.xml"
ADD_OR_MODIFY_PATTERN = re.compile(r'^\s*[M|A]\s+(.+[\.java|\.xml])\s*$')
# example: "R100    debug.java  test.java"
# example: "R109    src.xml  dest.xml"
RENAME_PATTERN = re.compile(r'^\s*R\d+\s+.+[\.java|\.xml]\s+(.+[\.java|\.xml])\s*$')

GROUP_INDEX_FILE_NAME = 1

DATE_PREFIX = 'Date:'
CHECKSTYLE_TAG = '[checked_3] '

CYGWIN_SYSTEM_PREFIX = 'CYGWIN'

# the first line of java body MUST be package declaration.
# for example: package com.wlqq.app;
JAVA_BODY_PATTERN = re.compile(r'^package.+$')
# the first line of java body MUST be body tag.
# for example:
#    <resources>
#    <selector xmlns:android="http://schemas.android.com/apk/res/android">
#    <LinearLayout
XML_BODY_PATTERN = re.compile(r'^<[a-zA-Z].+$')

XML_COPYRIGHT_TEMPLATE ="""\
<?xml version="1.0" encoding="utf-8"?>
<!-- Copyright (C) {} 贵阳货车帮科技有限公司 -->\n
"""

JAVA_COPYRIGHT_TEMPLATE ="""\
/*
 * Copyright (C) {} 贵阳货车帮科技有限公司
 */\n
"""

COMMIT_MESSAGE_FORMAT_DESCRIPTION="""
git commit message 格式不对。请修改后再post review

commit message format:
    <type>(<issue_id>): <subject>
    <BLANK LINE>
    <body>
    <BLANK LINE>
    <test affect>

Allowed <type>
    feat (feature)
    fix (bug fix)
    docs (documentation)
    style (formatting, missing semi colons, …)
    refactor
    test (when adding missing tests)
    chore (maintain)

比如：
    feat(ANDROID_INFRA-57): 修改copyright后自动commit文件。消除手动commit的困扰。

    扫描被修改的文件，发现copyright不对的，进行修改。然后自动提交commit相关改动。

    测试影响： copyright 相关测试
"""

# Allowed <type>
#    feat (feature)
#    fix (bug fix)
#    docs (documentation)
#    style (formatting, missing semi colons, …)
#    refactor
#    test (when adding missing tests)
#    chore (maintain)
ALLOWED_MESSAGE_TYPE = ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore']
MIN_MESSAGE_LINE_NUMBER = 5

INDEX_SUMMARY_LINE = 0
INDEX_FIRST_BLANK_LINE = 1
INDEX_BODY_LINE = 2

TEST_AFFECT = '测试影响'

JIRA_SERVER_URL = 'http://jira.56qq.cn/'


# the count of level, like ERROR, WARN
# such as '[WARN] D:\git_workspace\GasStationMerchant\GasStationMerchantApp\src\main\java\com\wlqq\checkout\CheckOutActivity.java:205'
def get_level_count(lines, level):
  return len(re.compile(r"\[%s\]" % level).findall(lines))


# output example:
#   commit 0bf74b02b7f9be98ebc5bddd59e71f95f2585633
#   Author: ZhouXu <xu.zhou1@56qq.com>
#   Date:   Thu May 25 14:59:19 2017 +0800
#
#   fix: 浮点数转化为长整型导致误差。目前前端已经限制只支持两位小数。所以目前只支持两位小数转化
#
#   M  src/main/java/com/wlqq/checkout/CheckOutActivity.java
#   D  src/main/java/com/wlqq/shift/activity/FixShiftSuccessActivity.java
#   A  src/main/java/com/wlqq/shift/activity/UnConfirmedShiftActivity.java
#   M  src/main/java/com/wlqq/shift/adapter/ConfirmOilPriceAdapter.java
#   A  src/main/res/values/strings.xml
#   R100    debug.java  test.java
#
# 获取java文件名列表
def get_commit_file_list(lines):

  list = []
  for line in lines:
    result = RENAME_PATTERN.match(line)
    if result:
      list.append(result.group(GROUP_INDEX_FILE_NAME))
      continue

    result = ADD_OR_MODIFY_PATTERN.match(line)
    if result:
      list.append(result.group(GROUP_INDEX_FILE_NAME))

  return list


# lines example:
#   feat(ANDROID_INFRA-57): 修改copyright后自动commit文件。消除手动commit的困扰。
#
#   扫描被修改的文件，发现copyright不对的，进行修改。然后自动提交commit相关改动。
#
#   测试影响： copyright 相关测试
#
# commit message format:
#    <type>(<issue_id>): <subject>
#    <BLANK LINE>
#    <body>
#    <BLANK LINE>
#    <test affect>
#
# Allowed <type>
#    feat (feature)
#    fix (bug fix)
#    docs (documentation)
#    style (formatting, missing semi colons, …)
#    refactor
#    test (when adding missing tests)
#    chore (maintain)
def check_commit_message_conventions(lines):
  if not lines:
    return None

  length = len(lines)

  if length < MIN_MESSAGE_LINE_NUMBER:
    print COMMIT_MESSAGE_FORMAT_DESCRIPTION
    return None

  issue_id = None
  subject = lines[INDEX_SUMMARY_LINE]
  # check line 1. should be "<type>(<issue_id>): <subject>"
  result = re.compile(r'^\s*(\w+)\s*\(\s*(.+)\s*\)\s*:(.+)$').match(subject)
  if result:
    type = result.group(1)

    if not type in ALLOWED_MESSAGE_TYPE:
      print '未知commit message type：' + type
      return None

    issue_id = result.group(2)
  else:
    print COMMIT_MESSAGE_FORMAT_DESCRIPTION
    return None

  blank = lines[INDEX_FIRST_BLANK_LINE]
  # check line 2. should be "<BLANK LINE>"
  if blank.strip():
    print COMMIT_MESSAGE_FORMAT_DESCRIPTION
    return None

  body = lines[INDEX_BODY_LINE]
  # check line 3. should be "<body>"
  if not body.strip():
    print COMMIT_MESSAGE_FORMAT_DESCRIPTION
    return None

  # find <test affect>
  i = length - 1
  while i > INDEX_BODY_LINE:
    if lines[i].strip() and lines[i].startswith(TEST_AFFECT):
      break
    i -= 1

  if i == INDEX_BODY_LINE:
    # can not find <test affect>
    print COMMIT_MESSAGE_FORMAT_DESCRIPTION
    return None

  # check blank line before test affect
  if not lines[i - 1].strip():
    return issue_id

  print COMMIT_MESSAGE_FORMAT_DESCRIPTION
  return None


def get_problem_count(files):
  hbt_dir = subprocess.check_output('git config hbt.dir', shell=True).strip()

  if platform.system().startswith(CYGWIN_SYSTEM_PREFIX):
    # change to cygwin path
    hbt_dir = subprocess.check_output('cygpath -m "' + hbt_dir + '"', shell=True).strip()

  jar_file = os.path.join(hbt_dir, CHECKSTYLE_JAR_FILE_NAME)
  config_file = os.path.join(hbt_dir, CHECKSTYLE_CONFIG_FILE_NAME)

  # check code command
  command = 'java -jar ' + jar_file + ' -c ' + config_file

  sum = 0
  for file in files:
    if is_java_file(file):
      print 'checking file: ' + file
      result = subprocess.check_output(command + ' ' + file, shell=True)

      count = get_level_count(result, LEVEL_ERROR)
      count += get_level_count(result, LEVEL_WARN)
      if count > 0:
        print "\n checkstyle failed: " + file

      sum += count

  return sum


def get_create_year(file):
  command = 'git log --follow --format=%ai --reverse -- {} | head -1'.format(file)

  # output example: 2015-11-10 15:44:29 +0800
  date_format = subprocess.check_output(command, shell=True)

  if len(date_format) == 0:
    return get_current_year()

  return date_format.split('-')[0]


def get_current_year():
  return time.strftime('%Y', time.localtime(time.time()))


def get_copyright(is_java, start, end):
  template = XML_COPYRIGHT_TEMPLATE

  if is_java:
    template = JAVA_COPYRIGHT_TEMPLATE

  if start == end:
    return template.format(start)

  return template.format(start + ' - ' + end)


def is_java_file(file):
  return file.find(JAVA_FILE_SUFFIX) != -1


def is_xml_file(file):
  return file.find(XML_FILE_SUFFIX) != -1


def is_body_start(is_java, line):
  if is_java:
    return JAVA_BODY_PATTERN.match(line)

  return XML_BODY_PATTERN.match(line)


def update_copyright(file):
  fileRead = open(file, 'r')
  lines = fileRead.readlines()
  fileRead.close()

  fileWrite = open(file, 'w')

  is_java = is_java_file(file)
  copyright = get_copyright(is_java, get_create_year(file), get_current_year())
  fileWrite.write(copyright)

  # skip until file body line
  need_skip = True
  for line in lines:
    if need_skip and is_body_start(is_java, line):
      need_skip = False

    if need_skip:
      continue;

    fileWrite.write(line)

  fileWrite.close()


def update_copyright_for_all(files):
  for file in files:
    print 'updating file: ' + file
    update_copyright(file)


def has_pending_changes():
  return '' != subprocess.check_output('git status --porcelain --untracked-files=no', shell=True)


def is_copyright_command(command):
  return 'copyright' == command


def is_land_command(command):
  return 'land' == command


def get_files(dir):
  list = []
  for root, dirs, files in os.walk(dir):
    for file in files:
      if is_java_file(file) or is_xml_file(file):
        list.append(os.path.join(root, file))

  return list


def check_argv_update(args):
  if len(args) != 3 or not os.path.isdir(args[2]):
    print 'Usage: hbt copyright <source_dir>'
    sys.exit(-1)


def check_argv_land(args):
  if len(args) != 3:
    print """
      Usage: hbt land <branch_name>
      branch_name is target branch name such as master, test17
      example: hbt land master
    """
    sys.exit(-1)


def push_change(branch_name):
  subprocess.call('git push origin HEAD:' + branch_name, shell=True)


def update_jira_comment(issue_id, commit_message):
  jira_user = subprocess.check_output('git config jira.user', shell=True).strip()
  jira_password = subprocess.check_output('git config jira.pwd', shell=True).strip()

  authed_jira = JIRA(server=(JIRA_SERVER_URL), basic_auth=(jira_user, jira_password))
  issue = authed_jira.issue(issue_id)
  authed_jira.add_comment(issue, commit_message)


def main():
  if is_copyright_command(sys.argv[1]):
    # format: hbt copyright <source_dir>
    check_argv_update(sys.argv)

    files = get_files(sys.argv[2])
    update_copyright_for_all(files)
    return

  if has_pending_changes():
    print '\nWARNING: 有未commit的文件。请commit后再发送review request'
    sys.exit(-1)

  commit_message = subprocess.check_output('git log --format=%B -n 1', shell=True)
  lines = commit_message.split('\n')
  issue_id = check_commit_message_conventions(lines)
  if not issue_id:
    sys.exit(-1)

  if is_land_command(sys.argv[1]):
    check_argv_land(sys.argv)

    # format: hbt land <branch_name>
    push_change(sys.argv[2])

    update_jira_comment(issue_id, commit_message)
    return

  summary = lines[INDEX_SUMMARY_LINE]

  commit_log = subprocess.check_output('git log --name-status -n 1', shell=True)
  commit_files = get_commit_file_list(commit_log.split('\n'))

  update_copyright_for_all(commit_files)
  # commit automatically after change copyright.
  subprocess.call('git commit -a --amend --no-edit', shell=True)

  count = get_problem_count(commit_files)
  if count > 0:
    print '\nWARNING: You must fix the errors and warnings first, then post review again'
    sys.exit(-1)

  # ignore the first argv
  rbt_command = 'rbt ' + ' '.join(sys.argv[1:])
  if summary:
    rbt_command += ' --summary "' + CHECKSTYLE_TAG + summary + '"'

  print 'running command: ' + rbt_command
  subprocess.call(rbt_command, shell=True)


if __name__ == '__main__':
  main()

