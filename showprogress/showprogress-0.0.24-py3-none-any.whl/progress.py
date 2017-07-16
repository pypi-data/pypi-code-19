from .memory import get_available_memory
from .memory import get_process_memory

import time
import sys
import datetime

def progress(iterable, head=None, item_length=0, memory_usage=True, memory_available=False, check_points=1, bar_character='#'):
    def to_list(iterable):
        items = [item for item in iterable]
        return len(items), items
    
    begin_time = time.time()
    if hasattr(iterable, '__len__'): n = len(iterable)
    elif hasattr(iterable, 'shape'): n = iterable.shape[0]
    else: n, iterable = to_list(iterable)
    
    for i, item in enumerate(iterable):
        yield item
        
        if check_points > 1 and (i % check_points) != 0:
            continue
            
        n_block = int(20 * i / n)
        n_bar = 20 - n_block
        process_time = time.time() - begin_time
        remained_time = (n - i) * process_time / (i+1) 
        
        args = (head+': ' if head else '', bar_character*n_block, '-'*n_bar, 100*i/n, '%', datetime.timedelta(seconds=int(process_time)), datetime.timedelta(seconds=int(remained_time)))
        message = '%s|%s%s| %.3f %s, [- %s, + %s]  ' % args
        
        if item_length > 0:
            message += (str(item)[:item_length] + '  ')
        if memory_usage:
            message += ('%.3f Gb used  ' % get_process_memory())
        if memory_available:
            message += ('%.3f Gb available  ' % get_available_memory())
        sys.stdout.write('\r%s' % message.strip())
        
    process_time = time.time() - begin_time
    print('\r%sdone. process time: %s' % (head + ' ' if head else '', datetime.timedelta(seconds=int(process_time))))
        