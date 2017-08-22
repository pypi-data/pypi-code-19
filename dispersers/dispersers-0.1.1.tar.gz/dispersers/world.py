from py_ibm import *
from trees_ibm.world import Tree_World
from dispersers import database_utils #import dispersers.database_utils
from dispersers.disperser_agents import PrimaryDisperser
#from plot_trees import plot_tree_pos
from tables import *
import json
import numpy as np



class Dispersers_World(Tree_World):

    def __init__(self,topology, parent_tree_class):
        super().__init__(topology)
        self.db=None
        self.seed_table=None
        self.ind_table=None
        self.sim_number=1
        self.parent_tree_class=parent_tree_class

    def setup_database(self, filename, sim_number):
        self.db=database_utils.open_database(filename,sim_number)
        try:
            self.db.get_node("/sim_{0}/dispersers/sys_lvl/Seeds".format(sim_number))
        except NoSuchNodeError:
            database_utils.create_tables(self.db,sim_number)

        self.seed_table=self.db.get_node("/sim_{0}/dispersers/sys_lvl/Seeds".format(sim_number))
        self.ind_table

    def add_seed_entry(self,tree_id,initial_x,
        initial_y,final_x,final_y,dispersal_type):
        seed_table=self.db.get_node("/sim_{0}/dispersers/sys_lvl/Seeds".format(self.sim_number))
        seed_r=seed_table.row

        seed_r["deposition_time"]=self.step
        seed_r["tree_id"]=tree_id
        seed_r["initial_x"]=initial_x
        seed_r["initial_y"]=initial_y
        seed_r["final_x"]=final_x
        seed_r["final_y"]=final_y
        seed_r["dispersal_type"]=dispersal_type

        seed_r.append()
        seed_table.flush()


    def add_ind_entry(self,ind_id,initial_x,
        initial_y,final_x,final_y,energy):
        ind_table=self.db.get_node("/sim_{0}/dispersers/ind_lvl/Ind".format(self.sim_number))
        ind_r=ind_table.row

        ind_r["time_stamp"]=self.step
        ind_r["ind_id"]=ind_id
        ind_r["initial_x"]=initial_x
        ind_r["initial_y"]=initial_y
        ind_r["final_x"]=final_x
        ind_r["final_y"]=final_y
        ind_r["energy"]=energy

        ind_r.append()
        ind_table.flush()


    def run_simulation(self,n):
        #self.db=database_utils.create_database(database_name,sim_number)

        for i in range(n):
            dispersers_ids=list(PrimaryDisperser.Instances.keys())
            for i in dispersers_ids:
                d=PrimaryDisperser.Instances.get(i)
                d.schedule2()
                self.add_ind_entry(ind_id=d.id,
                initial_x=d.previous_position[0],
                initial_y=d.previous_position[1],
                final_x=d.position[0],
                final_y=d.position[1],
                energy=d.energy)
            self.increment_time()
        self.db.close()




    def close_seeds_db(self):
        self.seeds_db.commit()
        self.seeds_db.close()

    def increase_dispersers_population(self):
        n=PrimaryDisperser.CalculatePopGrowth()
        self.create_dispersers(n)

    def create_dispersers(self,n):
        trees_for_dispersers=np.random.choice(list(self.parent_tree_class.Instances.keys()),size=n,replace=True)

        for i in range(n):
            tree_id=trees_for_dispersers[i]
            pos=self.parent_tree_class.Instances.get(tree_id).position
            PrimaryDisperser(position=pos,world=self,gut_passage_time=2, max_fruits=5, current_tree_id=tree_id)
