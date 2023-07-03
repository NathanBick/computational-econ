# here we create a network of automata
import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np  

# create a graph
G = nx.DiGraph()

# add 100 nodes with labels 0, 1, 2, ..., 99
G.add_nodes_from(range(100))

# now we assign a type variable to each node, red, blue, or white
for i in range(100):
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
for i in range(100):
    for j in range(100):
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
for i in range(100):
    G.nodes[i]['hours'] = 8
    if G.nodes[i]['type'] == 'red':
        G.nodes[i]['money'] = np.random.normal(1000, 100)
    elif G.nodes[i]['type'] == 'blue':
        G.nodes[i]['money'] = np.random.normal(500, 100)
    else:
        G.nodes[i]['money'] = np.random.normal(100, 10)

# now we define the production and utility functions for the nodes


# describe the distributions of money across the nodes
# we can do this by plotting a histogram

# first we get the money values
money = [G.nodes[i]['money'] for i in range(100)]

# now we plot the histogram
plt.hist(money, bins=20)
plt.savefig("money.png")
# clear
plt.clf()   

# draw the graph and save to file
# draw the nodes by the type
# red nodes are circles, blue nodes are squares, white nodes are triangles
# the size of the node is proportional to the amount of money

# make sure there isnt overlap between nodes
pos = nx.spring_layout(G)

# node size is proportional to money
nx.draw_networkx_nodes(G, pos, nodelist=[i for i in range(100) if G.nodes[i]['type'] == 'red'], node_color='r', node_shape='o')
nx.draw_networkx_nodes(G, pos, nodelist=[i for i in range(100) if G.nodes[i]['type'] == 'blue'], node_color='b', node_shape='s')
nx.draw_networkx_nodes(G, pos, nodelist=[i for i in range(100) if G.nodes[i]['type'] == 'white'], node_color='g', node_shape='^')

# draw the edges
nx.draw_networkx_edges(G, pos)

# save to file
# save to a large file so we can zoom in    
plt.savefig("graph.png", dpi=1000)

# save graph to file
nx.write_gexf(G, "graph.gexf")

