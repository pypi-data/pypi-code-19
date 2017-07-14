#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import networkx as nx
import matplotlib.pyplot as plt
import xml.etree.cElementTree as ET
import re
import fnmatch

# Script version
VERSION = '1.0'

# OptionParser imports
from optparse import OptionParser
from optparse import OptionGroup

# Options definition
parser = OptionParser(usage="%prog [options]\nVersion: " + VERSION)

main_grp = OptionGroup(parser, 'Main parameters')
main_grp.add_option('-i', '--input-file', help = 'sec_globauth.xml file containing the security rules', nargs = 1)
main_grp.add_option('-t', '--target', help = 'Program or file name you want to reach, globbing format accepted (Ex: cmd.exe, *cmd*)', nargs = 1)

opt_grp = OptionGroup(parser, 'Optional parameters')
opt_grp.add_option('-g', '--graph', help = 'Draw and show the graph with matplot', action = 'store_true', default = False)
opt_grp.add_option('-o', '--output-graph', help = 'Filename to save the png graph (Ex. -o test.png)', nargs = 1)
#opt_grp.add_option('-I', '--input-dir', help = '"Objects" entire directory, if you want GUID resolution and so', nargs = 1)

parser.option_groups.extend([main_grp, opt_grp])


def parse_sec_globauth(opts):
    """
        Extract enabled rules
    """
    global_rule_list = []
    
    tree = ET.ElementTree(file=opts.input_file)
    for elem in tree.iterfind(".//authfile[enabled='yes']"):
        authfile_current = {}
        for authfile in elem:
            authfile_current[authfile.tag] = authfile.text
            
            workspacecontrol_list = []
            # parsing workspace control
            if 'workspacecontrol' in authfile.tag:
                for workspace in authfile:
                    workspacecontrol_list.append(workspace.text)
            authfile_current['workspacecontrol'] = workspacecontrol_list
            
        global_rule_list.append(authfile_current)
    
    print "[+] Number of enabled rules: %s" % len(global_rule_list)
    
    return global_rule_list

def unify_label(label):
    """
        Take an authorized file name label and try to see if it stands for a known Windows binary
        If it's the case, just strip the abs path and keep the binary name
    """
    # stripping abs path for known Windows binaries
    if re.search('system32', label, re.IGNORECASE):
        label = label.split('\\')[-1]
        
    return label
    
def generate_orig_graph(rule_list, opts):
    """
        Connect the nodes following the rule list
    """
    G=nx.DiGraph()
    labels = {'.': '.'}
    
    for rule in rule_list:
        if rule['process'] and rule['authorizedfile'] and rule['guid']:
            # we want the label to keep the exact case
            process_name_label = rule['process']
            process_name = unify_label(process_name_label.lower())
            
            authorized_file_name_label = rule['authorizedfile']
            authorized_file_name = unify_label(rule['authorizedfile'].lower())
             
            labels[process_name] = process_name_label
            labels[authorized_file_name] = authorized_file_name_label
            
            # must add in lowercase to unify naming
            G.add_node('.', label=labels['.'])
            G.add_node(process_name, label=labels[process_name])
            G.add_node(authorized_file_name, label=labels[authorized_file_name])
            
            # implicit rule
            G.add_edge('.', process_name)
            G.add_edge(process_name, authorized_file_name, guid=rule['guid'], workspacecontrol=rule['workspacecontrol'])
    
    return G, labels

def search_path_to_target(nx_graph, opts):
    """
        Try to find a path to the target resource 
    """
    target_candidates = []
    possible_paths = []
    H = None
    
    # first step, find possible candidates for target
    for node, data in nx_graph.nodes_iter(data=True):
        if fnmatch.fnmatch(node, '*%s*' % (opts.target)):
            target_candidates.append(node)
            
    for target_candidate in target_candidates:
        has_path = nx.has_path(nx_graph, source='.', target=target_candidate)
        if has_path:
            # build the graph for the targeted resource, just for graphical purposes
            H=nx.DiGraph()
            
            # find all possible path
            possible_paths = nx.all_shortest_paths(nx_graph, source='.', target=target_candidate)
            for path in possible_paths:
                print "[+] Possible path to '%s': %s" % (target_candidate, path)
                H.add_edges_from(zip(path[::], path[1::]))
                
    return possible_paths, H
    
def draw_graph(nx_graph_orig, nx_graph_new, nx_labels, opts):
    """
        Try to draw a nice graph
    """
    # intersection between the original and targeted graph, with the trick to conserve attributes
    intersect_graph = nx_graph_orig.copy()
    if nx_graph_new:
        intersect_graph.remove_nodes_from(n for n in nx_graph_orig if n not in nx_graph_new)
    
    # printing edges data
    #print intersect_graph.edges(data=True)
    
    pos = nx.spectral_layout(intersect_graph)
    nx.draw_networkx_nodes(intersect_graph,pos,node_size=700)
    
    nx.draw_networkx_edges(intersect_graph, pos, width=6)
    
    nx.draw_networkx_labels(intersect_graph, pos, font_size=14, alpha=0, font_color='yellow')
    
    plt.axis('off')
    
    if opts.graph:
        plt.show()
    
    if opts.output_graph:
        figure_abs_path = os.path.join(os.getcwdu(), opts.output_graph)
        plt.savefig(figure_abs_path, format='png')
        print "[+] Graph saved at: %s" % figure_abs_path
    
    return

def main():
    """
        Dat main
    """
    
    options, arguments = parser.parse_args()
    
    if (options.input_file == None):
        parser.error('Please specify a valid input file')
        
    if (options.target == None):
        parser.error('Please specify a valid target filename')
    
    global_rule_list = parse_sec_globauth(options)
    
    orig_graph, labels = generate_orig_graph(global_rule_list, options)
    
    possible_path, search_graph = search_path_to_target(orig_graph, options)
    
    draw_graph(orig_graph, search_graph, labels, options)
    
    return
    
if __name__ == "__main__" :
    main()