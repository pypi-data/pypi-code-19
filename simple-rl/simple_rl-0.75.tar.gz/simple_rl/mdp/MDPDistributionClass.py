''' MDPDistributionClass.py: Contains the MDP Distribution Class. '''

import numpy as np
import random as r

class MDPDistribution(object):
    ''' Class for distributions over MDPs. '''
    def __init__(self, mdp_prob_dict):
        if len(mdp_prob_dict.values()) == 0:
            # Assume uniform?
            mdp_prob = 1.0 / len(mdp_prob_dict.keys())

        self.mdp_prob_dict = mdp_prob_dict


    def get_num_mdps():
        return len(self.mdp_prob_dict.keys())

    def sample(self, k=1):
        '''
        Args:
            k (int)

        Returns:
            (List of MDP): Samples @k mdps without replacement.
        '''

        sampled_mdp_id_list = np.random.multinomial(k, self.mdp_prob_dict.values()).tolist()
        indices = [i for i, x in enumerate(sampled_mdp_id_list) if x > 0]
        mdps_to_return = []

        for i in indices:
            for copies in xrange(sampled_mdp_id_list[i]):
                mdps_to_return.append(self.mdp_prob_dict.keys()[i])

        return mdps_to_return
        

def main():
    from simple_rl.tasks import GridWorldMDP, FourRoomMDP, ChainMDP, RandomMDP

    mdp_class = "grid"
    num_mdps = 5
    mdp_distr = {}
    mdp_prob = 1.0 / num_mdps
    height, width = 8, 8

    prob_list = [0.0, 0.1, 0.2, 0.3, 0.4]

    for i in range(num_mdps):
        new_mdp = {"grid":GridWorldMDP(width=width, height=5 + i, init_loc=(1, 1), goal_locs=r.sample(zip(range(1, width+1),[height]*width),2), is_goal_terminal=True),
                    "four_room":FourRoomMDP(width=8, height=8, goal_locs=r.sample([(1,8),(8,1),(8,8),(6,6),(6,1),(1,6)], 2)),
                    "chain":ChainMDP(num_states=10, reset_val=r.choice([0, 0.01, 0.05, 0.1])),
                    "random":RandomMDP(num_states=40, num_rand_trans=r.randint(1,10))}[mdp_class]

        mdp_distr[new_mdp] = prob_list[i]


    m = MDPDistribution(mdp_distr)
    m.sample()

if __name__ == "__main__":
    main()