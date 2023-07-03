# here we create a network of automata
import networkx as nx
import random
import numpy as np  
import pandas as pd

num_nodes = 100
num_iterations = 100

#### NOTES to self
# now no transactions are happening ... why?

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

# print the number of edges and number of nodes
print('Number of nodes: ', G.number_of_nodes())
print('Number of edges: ', G.number_of_edges())

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
    return G.nodes[node]['beta1'] * G.nodes[node]['work'] * G.nodes[node]['free'] + G.nodes[node]['beta2'] * G.nodes[node]['money'] + G.nodes[node]['beta0']
    #return G.nodes[node]['beta1'] * G.nodes[node]['hours'] + G.nodes[node]['beta2'] * G.nodes[node]['money'] + G.nodes[node]['beta3'] * sum([G.nodes[i]['money'] for i in G.neighbors(node)]) + G.nodes[node]['beta0']

def utility(node):
    return G.nodes[node]['alpha1'] * G.nodes[node]['free'] - G.nodes[node]['alpha1'] * G.nodes[node]['work'] + G.nodes[node]['alpha2'] * G.nodes[node]['money'] + G.nodes[node]['alpha0']
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
                
                  # check if the trade will make both nodes better off or if its impossible. 
                # check utility
                better_off = node1_utility_after_trade > node1_utility_before_trade and node2_utility_after_trade > node2_utility_before_trade

                # check if time variables are positive and consisten
                node1_time = G.nodes[node1]['free'] + G.nodes[node1]['work']
                node2_time = G.nodes[node2]['free'] + G.nodes[node2]['work']
                time_consistent = node1_time == 16 and node2_time == 16 and G.nodes[node1]['free'] >= 0 and G.nodes[node2]['free'] >= 0 and G.nodes[node1]['work'] >= 0 and G.nodes[node2]['work'] >= 0

                # check if money variables are positive and consistent
                node1_money = G.nodes[node1]['money']
                node2_money = G.nodes[node2]['money']
                money_consistent = node1_money >= 0 and node2_money >= 0

                # check if the trade will make both nodes better off, or if it is infeasible (node1 has no money to buy time or no time to sell)
                if not better_off or not time_consistent or not money_consistent:
                    # reverse the trade
                    G.nodes[node1]['free'] = G.nodes[node1]['free'] + 1
                    G.nodes[node1]['work'] = G.nodes[node1]['work'] - 1
                    G.nodes[node1]['money'] = G.nodes[node1]['money'] + price
                    G.nodes[node2]['free'] = G.nodes[node2]['free'] - 1
                    G.nodes[node2]['work'] = G.nodes[node2]['work'] + 1
                    G.nodes[node2]['money'] = G.nodes[node2]['money'] - price

                    return False
                
                else:
                    return True
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
                
                # check if the trade will make both nodes better off or if its impossible. 
                # check utility
                better_off = node1_utility_after_trade > node1_utility_before_trade and node2_utility_after_trade > node2_utility_before_trade

                # check if time variables are positive and consisten
                node1_time = G.nodes[node1]['free'] + G.nodes[node1]['work']
                node2_time = G.nodes[node2]['free'] + G.nodes[node2]['work']
                time_consistent = node1_time == 16 and node2_time == 16 and G.nodes[node1]['free'] >= 0 and G.nodes[node2]['free'] >= 0 and G.nodes[node1]['work'] >= 0 and G.nodes[node2]['work'] >= 0

                # check if money variables are positive and consistent
                node1_money = G.nodes[node1]['money']
                node2_money = G.nodes[node2]['money']
                money_consistent = node1_money >= 0 and node2_money >= 0

                # check if the trade will make both nodes better off, or if it is infeasible (node1 has no money to buy time or no time to sell)
                if not better_off or not time_consistent or not money_consistent:
                    # the trade will not make both nodes better off
                    # reverse the trade
                    G.nodes[node1]['free'] = G.nodes[node1]['free'] + 1
                    G.nodes[node1]['work'] = G.nodes[node1]['work'] - 1
                    G.nodes[node1]['money'] = G.nodes[node1]['money'] + price
                    G.nodes[node2]['free'] = G.nodes[node2]['free'] - 1
                    G.nodes[node2]['work'] = G.nodes[node2]['work'] + 1
                    G.nodes[node2]['money'] = G.nodes[node2]['money'] - price
                    
                    return False
                else:
                    return True

# function to determine the price. Go across a range of prices and attempt to trade at each price.
# once the price is found, return it.
# this will apply to pairs of nodes.
# TODO: make this work in both directions, up and down  
def find_price(node1, node2,price):
    counter = 0
    # transaction is a boolean that is true if the trade is successful
    while trade(node1, node2, price) == False:
        market_price = price
        price += 0.5
        counter += 1
        # if the price gets too far from the starting price, stop
        if price/market_price > 10:
            return market_price, False
        
        # if they can't trade at a price within 100 of the starting price, then they can't trade
        if counter > 100:
            return market_price, False
            
    return price, True

# now we define the simulation
# we run the simulation for 1000 steps
# at each step, we update the nodes, and then we trade
# crate a dataframe to store the data
# we want to make the price dynamic, but start with 1
# we want to make sure that we dont rerun the same pairs of nodes again in a turn, since our trade checks both directions of trade
starting_price = 100
prices = []
data = []
transactions = []
for i in range(num_iterations):
    print("Starting iteration " + str(i))
    print("Starting price is " + str(starting_price))
    # update the nodes
    update()  
    # count the transactions in a step
    transactions_in_step = 0          
    for j in range(num_nodes):
        for k in G.neighbors(j):
            # subset transaction to only include j,k,i
            subset_transactions = [x[2:5] for x in transactions]
            # check if we have already traded in this step using the j,k, and i values
            if [j,k,i] in subset_transactions or [k,j,i] in subset_transactions:
                continue
            
            price, transaction = find_price(j, k, starting_price)
            prices.append(price)
            # store price, node1, node2, and step
            transactions.append([price,transaction, j, k, i])
            if transaction == True:
                transactions_in_step += 1
    print("Number of transactions in step " + str(i) + " is " + str(transactions_in_step))
    # calculate the average price from this step
    average_price = sum(prices)/len(prices)
    # update the price for the next step
    # keep the older starting price
    prev_starting_price = starting_price
    starting_price = average_price
    # calculate the difference between the two prices
    price_difference = abs(starting_price - prev_starting_price)
    print("Price difference is " + str(price_difference))
    
    # save the data for each node to a long dataframe
    for j in range(num_nodes):
        data.append([i, j, G.nodes[j]['hours'], G.nodes[j]['free'], G.nodes[j]['work'], G.nodes[j]['money'], G.nodes[j]['type'], G.nodes[j]['happiness']])

    # if the price difference is less than a threshold, then we have reached equilibrium and we can stop the simulation
    if transactions_in_step == 0 or price_difference < 0.5:
        print("Equilibrium reached at step " + str(i))
        break
    
# write the transactions to a csv file
with open('transactions.csv', 'w') as f:
    names = ['price', "transaction",'node1', 'node2', 'step']
    df = pd.DataFrame(transactions)
    df.columns = names
    df.to_csv(f, header=True, index=False)

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

