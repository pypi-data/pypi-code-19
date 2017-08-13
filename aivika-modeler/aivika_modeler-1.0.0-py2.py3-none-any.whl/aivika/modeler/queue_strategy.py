# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

def expect_queue_strategy(queue_strategy):
    """Expect the queue strategy."""
    if queue_strategy in ['FCFS', 'LCFS', 'SIRO', 'StaticPriorities']:
        pass
    else:
        raise InvalidPortException('Unknown queue strategy: ' + str(queue_strategy) + ' (must be one of: FCFS, LCFS, SIRO or StaticPriorities)')

def is_priority_queue_strategy(queue_strategy):
    """Test whether the queue strategy is priority."""
    if queue_strategy in ['FCFS', 'LCFS', 'SIRO']:
        return False
    elif queue_strategy in ['StaticPriorities']:
        return True
    else:
        raise InvalidPortException('Unknown queue strategy: ' + str(queue_strategy) + ' (must be one of: FCFS, LCFS, SIRO or StaticPriorities)')
