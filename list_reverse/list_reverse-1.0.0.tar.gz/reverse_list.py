#names=["marry","john",["tom","jack",["1",2,3]]]
#numbers=[i for i in range(5)]
#duochong=[["a","b",['c','d'],'e',['g','gs',['ok','pop']]],'f']
def p_reverse(the_list):
    the_list.reverse()
    for each_item in the_list:
        if isinstance(each_item,list):
            p_reverse(each_item)

def print_reverse(the_list):
    
    p_reverse(the_list)
    print(the_list)





