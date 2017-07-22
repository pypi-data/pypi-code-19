# Copyright 2016 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from piglet import parser
samples = [
    '<html>',
    '<p></p>',
    '&amp;',
    '<a>x</a>',
    '<a><b></b></a>',
    '<img/>',
    '<img />',
    '<a href="foo"></a>',
    '<a  href="foo"></a>',
    '<a  href = "foo" ></a>',
    '<a href="foo" class=\'bar\'>x</a>',
    '<!-- a comment -->',
    '<p>hello <p>world',
    'fish &amp; chips',
    '<p>a</p>',
    '<html:p>a</html:p>',
    '<?php ?>',
    '<!DOCTYPE html>',
    '<!DOCTYPE html><script><![CDATA[ fish & chips ]]></script>',
]

for s in samples:
    print(s)
    print(parser(s).html())
