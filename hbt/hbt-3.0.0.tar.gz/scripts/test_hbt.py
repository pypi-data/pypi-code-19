#! /usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (C) 2017 贵阳货车帮科技有限公司
#

import unittest
import filecmp
import os
import shutil
from hbt import get_level_count, get_commit_file_list, get_problem_count, check_commit_message_conventions
from hbt import get_create_year, get_copyright, update_copyright, get_current_year, get_files
from hbt import is_java_file, is_xml_file, is_body_start, is_copyright_command, is_land_command
from hbt import LEVEL_ERROR, LEVEL_WARN, JAVA_COPYRIGHT_TEMPLATE, XML_COPYRIGHT_TEMPLATE

SRC_JAVA_FILE_NAME = 'src.java'
EXPECTED_JAVA_FILE_NAME = 'expected.java'

SRC_XML_FILE_NAME = 'src.xml'
EXPECTED_XML_FILE_NAME = 'expected.xml'

IS_JAVA_FILE = True
IS_XML_FILE = False

TEST_DIR = 'test'


class HbtTestCase(unittest.TestCase):
  def tearDown(self):
    if os.path.exists(SRC_JAVA_FILE_NAME):
      os.remove(SRC_JAVA_FILE_NAME)

    if os.path.exists(EXPECTED_JAVA_FILE_NAME):
      os.remove(EXPECTED_JAVA_FILE_NAME)

    if os.path.exists(SRC_XML_FILE_NAME):
      os.remove(SRC_XML_FILE_NAME)

    if os.path.exists(EXPECTED_XML_FILE_NAME):
      os.remove(EXPECTED_XML_FILE_NAME)

    if os.path.exists(TEST_DIR):
      shutil.rmtree(TEST_DIR)


  def test_get_level(self):
    problems = """
      Starting audit...
      [WARN] D:\git_workspace\GasStationMerchant\GasStationMerchantApp\src\main\java\com\wlqq\checkout\CheckOutActivity.java:205: 本行字符数 105个，最多：100个。 [LineLength]
      [WARN] D:\git_workspace\GasStationMerchant\GasStationMerchantApp\src\main\java\com\wlqq\checkout\CheckOutActivity.java:208: 本行字符数 110个，最多：100个。 [LineLength]
      [WARN] D:\git_workspace\GasStationMerchant\GasStationMerchantApp\src\main\java\com\wlqq\checkout\CheckOutActivity.java:268: 本行字符数 132个，最多：100个。 [LineLength]
      [WARN] D:\git_workspace\GasStationMerchant\GasStationMerchantApp\src\main\java\com\wlqq\checkout\CheckOutActivity.java:281:34: 避免空行。 [EmptyStatement]
      [ERROR] D:\git_workspace\GasStationMerchant\GasStationMerchantApp\src\main\java\com\wlqq\checkout\CheckOutActivity.java:292: 本行字符数 138个，最多：100个。 [LineLength]
      Audit done.
    """

    self.assertEquals(4, get_level_count(problems, LEVEL_WARN))
    self.assertEquals(1, get_level_count(problems, LEVEL_ERROR))

    no_problems = """
      Starting audit...
      Audit done.
    """
    self.assertEquals(0, get_level_count(no_problems, LEVEL_WARN))
    self.assertEquals(0, get_level_count(no_problems, LEVEL_ERROR))

    self.assertEquals(0, get_level_count('', LEVEL_WARN))
    self.assertEquals(0, get_level_count('', LEVEL_ERROR))


  def test_get_commit_file_list(self):
    commit_javas = """
    commit 0bf74b02b7f9be98ebc5bddd59e71f95f2585633
    Author: ZhouXu <xu.zhou1@56qq.com>
    Date:   Thu May 25 14:59:19 2017 +0800

    fix: 浮点数转化为长整型导致误差。目前前端已经限制只支持两位小数。所以目前只支持两位小数转化

M   src/main/java/com/wlqq/checkout/CheckOutActivity.java
D   src/main/java/com/wlqq/shift/activity/FixShiftSuccessActivity.java
A   src/main/java/com/wlqq/shift/activity/UnConfirmedShiftActivity.java
M   src/main/res/values/values.xml
D   src/main/res/values/colors.xml
A   src/main/res/values/strings.xml
R100    debug.java  test.java
R109    src.xml  dest.xml
    """

    list = get_commit_file_list(commit_javas.split('\n'))
    self.assertEquals(6, len(list))
    self.assertEquals('src/main/java/com/wlqq/checkout/CheckOutActivity.java', list[0])
    self.assertEquals('src/main/java/com/wlqq/shift/activity/UnConfirmedShiftActivity.java', list[1])
    self.assertEquals('src/main/res/values/values.xml', list[2])
    self.assertEquals('src/main/res/values/strings.xml', list[3])
    self.assertEquals('test.java', list[4])
    self.assertEquals('dest.xml', list[5])

    message_has_java = """
    commit 0bf74b02b7f9be98ebc5bddd59e71f95f2585633
    Author: ZhouXu <xu.zhou1@56qq.com>
    Date:   Thu May 25 14:59:19 2017 +0800

    fix: src/main/java/com/wlqq/checkout/Noisy.java

    M   src/main/java/com/wlqq/checkout/CheckOutActivity.java   
    D   src/main/java/com/wlqq/shift/activity/FixShiftSuccessActivity.java  
    A   src/main/java/com/wlqq/shift/activity/UnConfirmedShiftActivity.java  
    M   src/main/java/com/wlqq/shift/adapter/ConfirmOilPriceAdapter.java  
    R109    debug.java  test.java  
    """

    list = get_commit_file_list(message_has_java.split('\n'))
    self.assertEquals(4, len(list))
    self.assertEquals('src/main/java/com/wlqq/checkout/CheckOutActivity.java', list[0])
    self.assertEquals('src/main/java/com/wlqq/shift/activity/UnConfirmedShiftActivity.java', list[1])
    self.assertEquals('src/main/java/com/wlqq/shift/adapter/ConfirmOilPriceAdapter.java', list[2])
    self.assertEquals('test.java', list[3])

    without_files = """
    commit 0bf74b02b7f9be98ebc5bddd59e71f95f2585633
    Author: ZhouXu <xu.zhou1@56qq.com>
    Date:   Thu May 25 14:59:19 2017 +0800

    fix: 浮点数转化为长整型导致误差。目前前端已经限制只支持两位小数。所以目前只支持两位小数转化

    build.gradle
    README.md
    """
    list = get_commit_file_list(without_files.split('\n'))
    self.assertEquals(0, len(list))

    list = get_commit_file_list([])
    self.assertEquals(0, len(list))


  def test_check_commit_message_conventions(self):
    self.assertFalse(check_commit_message_conventions(None))
    self.assertFalse(check_commit_message_conventions([]))

    less_length = """\
fix(ANDROID_INFRA-57): 浮点数转化为长整型导致误差。目前前端已经限制只支持两位小数
    """
    self.assertIsNone(check_commit_message_conventions(less_length.split('\n')))

    unknown_type = """\
unknow(ANDROID_INFRA-57): 浮点数转化为长整型导致误差。目前前端已经限制只支持两位小数

body 描述

测试影响： 无
    """
    self.assertIsNone(check_commit_message_conventions(unknown_type.split('\n')))

    without_type = """\
(ANDROID_INFRA-57): 浮点数转化为长整型导致误差。目前前端已经限制只支持两位小数

body 描述

测试影响： 无
    """
    self.assertIsNone(check_commit_message_conventions(without_type.split('\n')))

    without_issue_id = """\
fix: 浮点数转化为长整型导致误差。目前前端已经限制只支持两位小数

body 描述

测试影响： 无
    """
    self.assertIsNone(check_commit_message_conventions(without_issue_id.split('\n')))

    missed_first_blank = """\
fix(ANDROID_INFRA-57): 浮点数转化为长整型导致误差。目前前端已经限制只支持两位小数
body 描述

测试影响： 无
    """
    self.assertIsNone(check_commit_message_conventions(missed_first_blank.split('\n')))

    missed_body = """\
fix(ANDROID_INFRA-57): 浮点数转化为长整型导致误差。目前前端已经限制只支持两位小数

测试影响： 无
    """
    self.assertIsNone(check_commit_message_conventions(missed_body.split('\n')))

    missed_last_blank = """\
fix(ANDROID_INFRA-57): 浮点数转化为长整型导致误差。目前前端已经限制只支持两位小数

body 描述
测试影响： 无
    """
    self.assertIsNone(check_commit_message_conventions(missed_last_blank.split('\n')))

    missed_test_affect = """\
fix(ANDROID_INFRA-57): 浮点数转化为长整型导致误差。目前前端已经限制只支持两位小数

body 描述

    """
    self.assertIsNone(check_commit_message_conventions(missed_test_affect.split('\n')))

    missed_key_word = """\
fix(ANDROID_INFRA-57): 浮点数转化为长整型导致误差。目前前端已经限制只支持两位小数

body 描述

需要小数组合测试
    """
    self.assertIsNone(check_commit_message_conventions(missed_key_word.split('\n')))

    valid_message = """\
fix(ANDROID_INFRA-57): 浮点数转化为长整型导致误差。目前前端已经限制只支持两位小数

body 描述

测试影响： 无
    """
    self.assertEquals('ANDROID_INFRA-57', check_commit_message_conventions(valid_message.split('\n')))

    multi_lines = """\
fix(ANDROID_INFRA-57): 浮点数转化为长整型导致误差。目前前端已经限制只支持两位小数

body 描述多行

并且描述可以包含空行

测试影响：
多行描述

可以包含空行
    """
    self.assertEquals('ANDROID_INFRA-57', check_commit_message_conventions(multi_lines.split('\n')))

    ending_blank_line = """\
fix(ANDROID_INFRA-57): 浮点数转化为长整型导致误差。目前前端已经限制只支持两位小数

body 描述多行

并且描述可以包含空行

测试影响：
多行描述

可以包含空行

    """
    self.assertEquals('ANDROID_INFRA-57', check_commit_message_conventions(ending_blank_line.split('\n')))


  def test_get_problem_count(self):
    self.assertEquals(2, get_problem_count(['TestHasWarns.java']))
    self.assertEquals(0, get_problem_count(['TestNoWarn.java']))


  def test_get_create_year(self):
    self.assertEquals('2017', get_create_year('TestHasWarns.java'))
    self.assertEquals('2017', get_create_year('TestNoWarn.java'))
    self.assertEquals('2017', get_create_year('Unexisted.java'))


  def test_get_copyright(self):
    self.assertEquals(JAVA_COPYRIGHT_TEMPLATE.format('2016'), get_copyright(IS_JAVA_FILE, '2016', '2016'))
    self.assertEquals(JAVA_COPYRIGHT_TEMPLATE.format('2015 - 2017'), get_copyright(IS_JAVA_FILE, '2015', '2017'))

    self.assertEquals(XML_COPYRIGHT_TEMPLATE.format('2016'), get_copyright(IS_XML_FILE, '2016', '2016'))
    self.assertEquals(XML_COPYRIGHT_TEMPLATE.format('2015 - 2017'), get_copyright(IS_XML_FILE, '2015', '2017'))


  def test_is_java_file(self):
    self.assertTrue(is_java_file('TestNoWarn.java'))
    self.assertTrue(is_java_file('src/main/java/com/wlqq/checkout/CheckOutActivity.java'))
    self.assertFalse(is_java_file('build.gradle'))
    self.assertFalse(is_java_file('colors.xml'))
    self.assertFalse(is_java_file('src/main/res/values/colors.xml'))


  def test_is_xml_file(self):
    self.assertFalse(is_xml_file('TestNoWarn.java'))
    self.assertFalse(is_xml_file('src/main/java/com/wlqq/checkout/CheckOutActivity.java'))
    self.assertFalse(is_xml_file('build.gradle'))
    self.assertTrue(is_xml_file('colors.xml'))
    self.assertTrue(is_xml_file('src/main/res/values/colors.xml'))


  def test_is_copyright_command(self):
    self.assertFalse(is_copyright_command('post'))
    self.assertFalse(is_copyright_command('land'))
    self.assertTrue(is_copyright_command('copyright'))


  def test_is_land_command(self):
    self.assertFalse(is_land_command('post'))
    self.assertTrue(is_land_command('land'))
    self.assertFalse(is_land_command('copyright'))


  def test_is_body_start(self):
    self.assertTrue(is_body_start(IS_JAVA_FILE, 'package com.wlqq.app;'))
    self.assertFalse(is_body_start(IS_JAVA_FILE, 'public abstract class BaseProgressActivity {'))

    self.assertFalse(is_body_start(IS_XML_FILE, 'package com.wlqq.app;'))

    self.assertTrue(is_body_start(IS_XML_FILE, '<resources>'))
    self.assertTrue(is_body_start(IS_XML_FILE, '<LinearLayout'))
    self.assertTrue(is_body_start(IS_XML_FILE, '<selector xmlns:android="http://schemas.android.com/apk/res/android">'))

    self.assertFalse(is_body_start(IS_XML_FILE, 'android:layout_width="match_parent"'))
    self.assertFalse(is_body_start(IS_XML_FILE, '<?xml version="1.0" encoding="utf-8"?>'))
    self.assertFalse(is_body_start(IS_XML_FILE, '<!-- Copyright (C) 2017 贵阳货车帮科技有限公司 -->'))
    self.assertFalse(is_body_start(IS_JAVA_FILE, '<resources>'))


  def create_file(self, dir, file_name):
    file = open(os.path.join(dir, file_name), 'a')
    file.close()


  def test_get_files(self):
    root = os.getcwd()

    test_dir_path = os.path.join(root, TEST_DIR)
    os.mkdir(test_dir_path)

    self.create_file(test_dir_path, SRC_JAVA_FILE_NAME)
    self.create_file(test_dir_path, SRC_XML_FILE_NAME)
    self.create_file(test_dir_path, 'unknown_file')

    files = get_files(root)
    self.assertEquals(4, len(files))
    self.assertEquals(os.path.join(root, 'TestHasWarns.java'), files[0])
    self.assertEquals(os.path.join(root, 'TestNoWarn.java'), files[1])

    self.assertEquals(os.path.join(test_dir_path, 'src.java'), files[2])
    self.assertEquals(os.path.join(test_dir_path, 'src.xml'), files[3])


  def test_update_copyright(self):
    java_content = """\
package com.wlqq.data.net;

import com.raizlabs.android.dbflow.annotation.NotNull;
import com.wlqq.data.request.LoginParams;
import com.wlqq.login.model.Session;
"""

    added_copyright = JAVA_COPYRIGHT_TEMPLATE.format(get_current_year())

    fileWrite = open(SRC_JAVA_FILE_NAME, 'w')
    fileWrite.write(java_content)
    fileWrite.close()

    fileWrite = open(EXPECTED_JAVA_FILE_NAME, 'w')
    fileWrite.write(added_copyright)
    fileWrite.write(java_content)
    fileWrite.close()

    self.assertFalse(filecmp.cmp(EXPECTED_JAVA_FILE_NAME, SRC_JAVA_FILE_NAME))
    update_copyright(SRC_JAVA_FILE_NAME)
    self.assertTrue(filecmp.cmp(EXPECTED_JAVA_FILE_NAME, SRC_JAVA_FILE_NAME))

    xml_content = """\
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".settings.AboutUsActivity">
"""

    added_copyright = XML_COPYRIGHT_TEMPLATE.format(get_current_year())

    fileWrite = open(SRC_XML_FILE_NAME, 'w')
    fileWrite.write(xml_content)
    fileWrite.close()

    fileWrite = open(EXPECTED_XML_FILE_NAME, 'w')
    fileWrite.write(added_copyright)
    fileWrite.write(xml_content)
    fileWrite.close()

    self.assertFalse(filecmp.cmp(EXPECTED_XML_FILE_NAME, SRC_XML_FILE_NAME))
    update_copyright(SRC_XML_FILE_NAME)
    self.assertTrue(filecmp.cmp(EXPECTED_XML_FILE_NAME, SRC_XML_FILE_NAME))


if __name__ == '__main__':
  unittest.main()
