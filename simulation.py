# here we create a network of automata
import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np  
import pandas as pd

num_nodes = 100
num_iterations = 100
num_trades = 0

#### NOTES to self
# no trades are happening, but the money is changing. I would expect an increase due to the production, but there is a drop
# why arent trades happening?

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
# this includes a uniform allocation of 16 hours to each node, and a random amount of money, determined by type
# there is work hours, and free hours. Free + work = 16. 
# for red, the money N(1000, 100)
# for blue, the money is N(500, 100) 
# for white, the money is N(100, 10)
for i in range(num_nodes):
    # time allocation
    G.nodes[i]['hours'] = 16
    G.nodes[i]['free'] = 8
    G.nodes[i]['work'] = G.nodes[i]['hours'] - G.nodes[i]['free']
    # money allocation
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
    return G.nodes[node]['beta1'] * G.nodes[node]['work'] + G.nodes[node]['beta2'] * G.nodes[node]['money'] + G.nodes[node]['beta0']
    #return G.nodes[node]['beta1'] * G.nodes[node]['hours'] + G.nodes[node]['beta2'] * G.nodes[node]['money'] + G.nodes[node]['beta3'] * sum([G.nodes[i]['money'] for i in G.neighbors(node)]) + G.nodes[node]['beta0']

def utility(node):
    return G.nodes[node]['alpha1'] * G.nodes[node]['free'] + G.nodes[node]['alpha2'] * G.nodes[node]['money'] + G.nodes[node]['alpha0']
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
def trade(node1, node2, price,num_trades):
    # check utility of node1 and node2 before trade
    node1_utility_before_trade = utility(node1)
    node2_utility_before_trade = utility(node2)

    # a trade is when a node buys more free time from another node in exchange for money
    # to start, we assume that the node with more money is the one buying time

    # check which node has more money
    if G.nodes[node1]['money'] > G.nodes[node2]['money']:
        # node1 is buying time from node2
        # check how much time node2 has to sell
        if G.nodes[node2]['free'] > 0:
            # node2 has time to sell
            # check how much money node1 has to buy time
            if G.nodes[node1]['money'] > price:
                # do the trade. Then see if both better off. If so, keep it. If not, reverse it.
                # get starting utility of node1 and node2
                node1_utility_before_trade = utility(node1)
                node2_utility_before_trade = utility(node2)
                # do the trade
                G.nodes[node1]['free'] = G.nodes[node1]['free'] - 1
                G.nodes[node1]['work'] = G.nodes[node1]['work'] + 1
                G.nodes[node1]['money'] = G.nodes[node1]['money'] - price
                G.nodes[node2]['free'] = G.nodes[node2]['free'] + 1
                G.nodes[node2]['work'] = G.nodes[node2]['work'] - 1
                G.nodes[node2]['money'] = G.nodes[node2]['money'] + price
                
                # calculate utility of node1 and node2 after trade
                node1_utility_after_trade = utility(node1)
                node2_utility_after_trade = utility(node2)
                # increase the trade counter
                num_trades += 1
                # check if the trade will make both nodes better off
                if not (node1_utility_after_trade > node1_utility_before_trade and node2_utility_after_trade > node2_utility_before_trade):
                    # reverse the trade
                    G.nodes[node1]['free'] = G.nodes[node1]['free'] + 1
                    G.nodes[node1]['work'] = G.nodes[node1]['work'] - 1
                    G.nodes[node1]['money'] = G.nodes[node1]['money'] + price
                    G.nodes[node2]['free'] = G.nodes[node2]['free'] - 1
                    G.nodes[node2]['work'] = G.nodes[node2]['work'] + 1
                    G.nodes[node2]['money'] = G.nodes[node2]['money'] - price
    else:
        # node2 is buying time from node1
        # check how much time node1 has to sell
        if G.nodes[node1]['free'] > 0:
            # node1 has time to sell
            # check how much money node2 has to buy time
            if G.nodes[node2]['money'] > price:
                # do the trade. Then see if both better off. If so, keep it. If not, reverse it.
                # get starting utility of node1 and node2
                node1_utility_before_trade = utility(node1)
                node2_utility_before_trade = utility(node2)
                # do the trade
                G.nodes[node1]['free'] = G.nodes[node1]['free'] - 1
                G.nodes[node1]['work'] = G.nodes[node1]['work'] + 1
                G.nodes[node1]['money'] = G.nodes[node1]['money'] - price
                G.nodes[node2]['free'] = G.nodes[node2]['free'] + 1
                G.nodes[node2]['work'] = G.nodes[node2]['work'] - 1
                G.nodes[node2]['money'] = G.nodes[node2]['money'] + price
                
                # calculate utility of node1 and node2 after trade
                node1_utility_after_trade = utility(node1)
                node2_utility_after_trade = utility(node2)
                num_trades += 1
                # check if the trade will make both nodes better off
                if not (node1_utility_after_trade > node1_utility_before_trade and node2_utility_after_trade > node2_utility_before_trade):
                    # the trade will not make both nodes better off
                    # reverse the trade
                    G.nodes[node1]['free'] = G.nodes[node1]['free'] + 1
                    G.nodes[node1]['work'] = G.nodes[node1]['work'] - 1
                    G.nodes[node1]['money'] = G.nodes[node1]['money'] + price
                    G.nodes[node2]['free'] = G.nodes[node2]['free'] - 1
                    G.nodes[node2]['work'] = G.nodes[node2]['work'] + 1
                    G.nodes[node2]['money'] = G.nodes[node2]['money'] - price
    
# now we define the simulation
# we run the simulation for 1000 steps
# at each step, we update the nodes, and then we trade
# crate a dataframe to store the data
# we want to make the price dynamic, but start with 1
price = 1
data = []
for i in range(num_iterations):
    update()            
    for j in range(num_nodes):
        for k in G.neighbors(j):
            trade(j, k, price,num_trades)
    print(i)
    # save the data for each node to a long dataframe
    for j in range(num_nodes):
        data.append([i, j, G.nodes[j]['hours'], G.nodes[j]['free'], G.nodes[j]['work'], G.nodes[j]['money'], G.nodes[j]['type'], G.nodes[j]['happiness']])

print(num_trades)

# write the data to a csv file
with open('simulation_data.csv', 'w') as f:
    # add names to the columns
    fieldnames = ['step', 'id', 'hours','free','work', 'money', 'type', 'happiness']
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

