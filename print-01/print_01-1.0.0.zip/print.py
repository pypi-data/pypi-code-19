# 定义一个函数用来按层级打印多级列表

def print_lol(the_list, indence=False, level=0):
    # 遍历列表，如果发现下一层级就递归

    for each_iterm in the_list:
        if isinstance(each_iterm, list):
            print_lol(each_iterm, indence, level+1)

        else:
            # 如果需要缩进就执行
            if indence:
                    print('\t'*level, end='')
            print(each_iterm)
