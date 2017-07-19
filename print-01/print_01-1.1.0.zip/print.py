# 定义一个函数用来按层级打印多级列表

import sys

def print_lol(the_list, indent=False, level=0, fh=sys.stdout):
    # 遍历列表，如果发现下一层级就递归

    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level+1, fh)

        else:
            # 如果需要缩进就执行
            if indent:
                for tab_stop in range(level):
                    print('\t', end='', file=fh)
            print(each_item, file=fh)
