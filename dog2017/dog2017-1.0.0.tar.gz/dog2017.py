"""这是一个例子"""
def print_lol(the_list):
        """fuck"""
        for each_item in the_list:
                if isinstance(each_item,list):
                        print_lol(each_item)
                else:
                        print(each_item)
                        
                        
		
	
