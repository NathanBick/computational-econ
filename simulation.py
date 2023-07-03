# here we create a network of automata
import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np  
import pandas as pd

num_nodes = 100
num_iterations = 100

#### NOTES to self
# currently, there is an early drop in money - where does this come from?
# need to look more closely at the trade function

# create a graph
G = nx.DiGraph()

# add 100 nodes with labels 0, 1, 2, ..., 99
G.add_nodes_from(range(num_nodes))

# add id variable to each node
for i in range(num_nodes):
    G.nodes[i]['id'] = i

# now we assign a type variable to each node, red, blue, or white
for i in range(num_nodes):
    if i < 20:
        G.nodes[i]['type'] = 'red'
    elif i < 50:
        G.nodes[i]['type'] = 'blue'
    else:
        G.nodes[i]['type'] = 'white'

# now we add edges between nodes
# this is done randomnly. The probability depends on the types of the nodes
# if the nodes are the same type, the probability is 0.4
# if the pair is red and blue, the probability is 0.2
# if one of the nodes is white, the probability is 0.01
# the edges are undirected, so we add both directions
for i in range(num_nodes):
    for j in range(num_nodes):
        if i != j:
            if G.nodes[i]['type'] == G.nodes[j]['type']:
                if random.random() < 0.4:
                    G.add_edge(i,j)
                    G.add_edge(j,i)
            elif G.nodes[i]['type'] == 'red' and G.nodes[j]['type'] == 'blue':
                if random.random() < 0.2:
                    G.add_edge(i,j)
                    G.add_edge(j,i)
            elif G.nodes[i]['type'] == 'blue' and G.nodes[j]['type'] == 'red':
                if random.random() < 0.2:
                    G.add_edge(i,j)
                    G.add_edge(j,i)
            else:
                if random.random() < 0.01:
                    G.add_edge(i,j)
                    G.add_edge(j,i)

# now we assign the attributes to the nodes
# this includes a uniform allocation of 8 hours to each node, and a random amount of money, determined by type
# for red, the money N(1000, 100)
# for blue, the money is N(500, 100) 
# for white, the money is N(100, 10)
for i in range(num_nodes):
    G.nodes[i]['hours'] = 8
    if G.nodes[i]['type'] == 'red':
        G.nodes[i]['money'] = np.random.normal(1000, 10)
    elif G.nodes[i]['type'] == 'blue':
        G.nodes[i]['money'] = np.random.normal(500, 10)
    else:
        G.nodes[i]['money'] = np.random.normal(100, 10)

# now we define the production and utility functions for the nodes
# the production function: money = beta1 * hours + beta2 * money + beta3 * neighbors' money + beta0
# the utility function: utility = alpha1 * hours + alpha2 * money + alpha3 * neighbors' money + alpha0
# the parameters are chosen randomly from truncated normal distributions with mean 0.5, sd 1, and truncated at 0 and 1
for i in range(num_nodes):
    # if outside range of 0 and 1, truncate
    G.nodes[i]['beta1'] = max(min(max(np.random.normal(0.5,1), 0), 1), 0)
    G.nodes[i]['beta2'] = max(min(max(np.random.normal(0.5,1), 0), 1), 0)
    G.nodes[i]['beta3'] = max(min(max(np.random.normal(0.5,1), 0), 1), 0)
    G.nodes[i]['beta0'] = max(min(max(np.random.normal(0.5,1), 0), 1), 0)
    G.nodes[i]['alpha1'] = max(min(max(np.random.normal(0.5,1), 0), 1), 0)
    G.nodes[i]['alpha2'] = max(min(max(np.random.normal(0.5,1), 0), 1), 0)
    G.nodes[i]['alpha3'] = max(min(max(np.random.normal(0.5,1), 0), 1), 0)
    G.nodes[i]['alpha0'] = max(min(max(np.random.normal(0.5,1), 0), 1), 0)

# now we define the production and utility functions
# for now we do not include the neighbors' information in the calculation
def production(node):
    return G.nodes[node]['beta1'] * G.nodes[node]['hours'] + G.nodes[node]['beta2'] * G.nodes[node]['money'] + G.nodes[node]['beta0']
    #return G.nodes[node]['beta1'] * G.nodes[node]['hours'] + G.nodes[node]['beta2'] * G.nodes[node]['money'] + G.nodes[node]['beta3'] * sum([G.nodes[i]['money'] for i in G.neighbors(node)]) + G.nodes[node]['beta0']

def utility(node):
    return G.nodes[node]['alpha1'] * G.nodes[node]['hours'] + G.nodes[node]['alpha2'] * G.nodes[node]['money'] + G.nodes[node]['alpha0']
    #return G.nodes[node]['alpha1'] * G.nodes[node]['hours'] + G.nodes[node]['alpha2'] * G.nodes[node]['money'] + G.nodes[node]['alpha3'] * sum([G.nodes[i]['money'] for i in G.neighbors(node)]) + G.nodes[node]['alpha0']

# now we define the update function across the nodes
def update():
    for i in range(num_nodes):
        G.nodes[i]['money'] = production(i)
        G.nodes[i]['happiness'] = utility(i)

# define trade function
# this function takes in two nodes, and transfers either money or time from one to the other
# the max of hours is 16
# for each combo of ndoes, check if a trade will make both nodes better off - if so, do it
# price is the price of 1 hour of time in terms of money
def trade(node1, node2, price):
    # check utility of node1 and node2 before trade
    utility1 = utility(node1)
    utility2 = utility(node2)

    # attempt to trade in each direction
    # if the trade makes both nodes better off, do it
    # node 1 sells time to node 2
    if G.nodes[node1]['hours'] > 0 and G.nodes[node2]['money'] > 0:
        G.nodes[node1]['hours'] -= 1
        G.nodes[node2]['hours'] += 1
        G.nodes[node1]['money'] += price
        G.nodes[node2]['money'] -= price
        if utility(node1) < utility1 and utility(node2) < utility2:
            G.nodes[node1]['hours'] += 1
            G.nodes[node2]['hours'] -= 1
            G.nodes[node1]['money'] -= price
            G.nodes[node2]['money'] += price
    # node 2 sells time to node 1
    # if G.nodes[node2]['hours'] > 0 and G.nodes[node1]['money'] > 0:
    #     G.nodes[node2]['hours'] -= 1
    #     G.nodes[node1]['hours'] += 1
    #     G.nodes[node2]['money'] += price
    #     G.nodes[node1]['money'] -= price
    #     if utility(node1) < utility1 and utility(node2) < utility2:
    #         G.nodes[node2]['hours'] += 1
    #         G.nodes[node1]['hours'] -= 1
    #         G.nodes[node2]['money'] -= price
    #         G.nodes[node1]['money'] += price

# now we define the simulation
# we run the simulation for 1000 steps
# at each step, we update the nodes, and then we trade
# crate a dataframe to store the data
data = []
for i in range(num_iterations):
    update()            
    for j in range(num_nodes):
        for k in G.neighbors(j):
            trade(j, k, 10)
    print(i)
    # save the data for each node to a long dataframe
    for j in range(num_nodes):
        data.append([i, j, G.nodes[j]['hours'], G.nodes[j]['money'], G.nodes[j]['type'], G.nodes[j]['happiness']])

# write the data to a csv file
with open('simulation_data.csv', 'w') as f:
    # add names to the columns
    fieldnames = ['step', 'id', 'hours', 'money', 'type', 'happiness']
    df = pd.DataFrame(data)
    df.columns = fieldnames
    df.to_csv(f, header=True, index=False)

# describe the distributions of money across the nodes
# we can do this by plotting a histogram

# # first we get the money values
# money = [G.nodes[i]['money'] for i in range(100)]

# # now we plot the histogram
# plt.hist(money, bins=20)
# plt.savefig("money.png")
# # clear
# plt.clf()   

# # draw the graph and save to file
# # draw the nodes by the type
# # red nodes are circles, blue nodes are squares, white nodes are triangles
# # the size of the node is proportional to the amount of money

# # make sure there isnt overlap between nodes
# pos = nx.spring_layout(G)

# # node size is proportional to money
# nx.draw_networkx_nodes(G, pos, nodelist=[i for i in range(100) if G.nodes[i]['type'] == 'red'], node_color='r', node_shape='o')
# nx.draw_networkx_nodes(G, pos, nodelist=[i for i in range(100) if G.nodes[i]['type'] == 'blue'], node_color='b', node_shape='s')
# nx.draw_networkx_nodes(G, pos, nodelist=[i for i in range(100) if G.nodes[i]['type'] == 'white'], node_color='g', node_shape='^')

# # draw the edges
# nx.draw_networkx_edges(G, pos)

# # save to file
# # save to a large file so we can zoom in    
# plt.savefig("graph.png", dpi=1000)

# # save graph to file
# nx.write_gexf(G, "graph.gexf")

