import numpy as np
from math import floor,atan2,degrees,sin,cos,radians, isnan
from operator import methodcaller

class World(object):

    """ Provide observer methods and control the schedule and execution of simulations.

    Args:
        topology (Rectangular_Grid instance): grid object on which agents will live.
        steps_in_day (int): number of steps in each day.

    Attributes:
        topology (Rectangular_Grid instance): grid object on which agents will live.
        steps_in_day (int): number of steps in each day.
        day (int): current day.
        step (int): current step.

    Usage:
        >>> grid01=Rectangular_Grid(x_max=5,y_max=5,ndim=1,dim_names=["light_intensity"])
        >>> world01=World(topology=grid01)
        >>> print(world01)
        World object

    """

    def __repr__(self):
        return "World object"
    def __init__(self,topology,steps_in_day=1440):
        self.topology=topology
        self.day=0
        self.step=0
        self.steps_in_day=steps_in_day
       	#self.all_agents={}


    def active_agents(self):
    	""" Return a list of active agents. """
    	pass

    def run_simulation(self,n):
        """ Run the schedule n times.

            Note: actions to be performed before or after all the schedule could be included here. An example would be writing model outputs to a file every 10 steps.

        Args:
                n (int): number of times (repetitions) the schedule should be run.
        Returns:
            None.

        """
        for i in range(n):
            self.run_schedule()

    def run_schedule(self):
    	""" This method is supposed to be overridden.
    	It should include the schedules of agent classes plus any other action taken by the world, such as incrementing time or calculating summary statistics
    	"""
    	self.increment_time()



    def create_agents(self,agent_type,n,pos=None, **kwargs):
        """ Create 'n' 'agent_type' agents.

        Args:
            agent_type (class): the type (class) of agents to be created
            n (int): number of agents to be created
            pos (list,None): a list of 'n' tuples '(x,y)' with the coordinates in which agents will be created. If set to None, agents are created in random positions.
            kwargs: the arguments to be passed to the 'agent_type' class. All agents will be created with this same set of arguments.

        Returns:
            None.
        """
        if pos==None:
            for i in range(n):
                random_pos=(np.random.rand()*self.topology.x_max,np.random.rand()*self.topology.y_max)
                agent_type(position=random_pos,**kwargs)
        else:
            for i in range(n):
                agent_type(position=pos[i],**kwargs)


    def ask(self, agents, methodname, *args, **kwargs):
        """ Make 'agents' execute the 'methodname'

        Args:
            agents (list): A list of agents (instances).
            methodname (str): name of the methods to be executed.
            args: argumrntd to br passed to 'methodname.
            kwargs:keyword arguments to be passed to 'methodname'

        Returns:
            None.
        """
        f = methodcaller(methodname, *args, **kwargs)
        for agent in agents:
                f(agent)


    def increment_time(self):
        """ Increment step and day counters

        Returns:
            None.
        """
        self.step+=1
        if self.step==self.steps_in_day:
            self.step=0
            self.day+=1
