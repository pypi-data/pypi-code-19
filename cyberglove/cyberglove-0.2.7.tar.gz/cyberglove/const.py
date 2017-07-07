import os

joint_names = ['WRJ1', 'WRJ0',
               'FFJ3', 'FFJ2', 'FFJ1', 'FFJ0',
               'MFJ3', 'MFJ2', 'MFJ1', 'MFJ0',
               'RFJ3', 'RFJ2', 'RFJ1', 'RFJ0',
               'LFJ4', 'LFJ3', 'LFJ2', 'LFJ1', 'LFJ0',
               'THJ4', 'THJ3', 'THJ2', 'THJ1', 'THJ0']


sensors_influence = {0: ["TH"],
                     1: ["TH"],
                     2: ["THJ2", "THJ1", "THJ0"],
                     3: ["THJ2", "THJ1", "THJ0", "FFJ3", "FFJ2"],
                     4: ["FFJ3", "FFJ2"],
                     5: ["FFJ1", "FFJ0"],
                     6: ["FFJ1", "FFJ0"],
                     7: ["MFJ3", "MFJ2"],
                     8: ["MFJ1", "MFJ0"],
                     9: ["MFJ1", "MFJ0"],
                     10:["FFJ3", "FFJ2", "MFJ3", "MFJ2"],
                     11:["RFJ3", "RFJ2"],
                     12:["RFJ1", "RFJ0"],
                     13:["RFJ1", "RFJ0"],
                     14:["MFJ3", "MFJ2", "RFJ3", "RFJ2"],
                     15:["LFJ4", "LFJ3", "LFJ2"],
                     16:["LFJ1", "LFJ0"],
                     17:["LFJ1", "LFJ0"],
                     18:["RFJ3", "RFJ2", "LFJ4", "LFJ3", "LFJ2"],
                     19:["LFJ3", "RFJ3", "MFJ3", "LFJ3"],
                     20:["WR"],
                     21:["WR"]}


# Figure out what directory the configuration files will be in
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
