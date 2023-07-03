# Computational Economics

This repository contains experiments in computational economics. It is my personal conviction that economics should become more of an interdisciplinary science with strong links to computer science, data science, and mathematics in addition to the fields of history, sociology, and psychology. This repository is my attempt to contribute to this development.

## Contents

Currently, I've attemtped to implement the following models:

* language model 
* cellular automata


## Cellular Automata

Inspiration from Conway's Game of Life. The model is a cellular automata model with a graph setup and a few rules:

* Each node has an allocation of **time**, **money**, and **happiness**.
* Each node has a **production function** that determines how much time it takes to produce a unit of money. This is assumed to be linear, but the slope can vary between nodes. This will be determined by a random variable. 
* Each node has a **utility function** that determines how much happiness it gets from consuming a unit of money or time. Similarly to the production function, this is assumed to be linear, but the slope can vary between nodes. Generally, the slope for time is assumed to be higher than the slope for money.
* Nodes wish to maximize their utility.
* Nodes can trade with their "neighbors", other nodes to which they are connected in the graph. We will assume that the graph is undirected and random. However, there will be a **type** variable for each node which represents groups in society. This will be used to determine the probability of a connection between two nodes.
* Nodes can trade time for money and vice versa. The exchange rate is determined by the production functions of the two nodes. That is, if a node has money, it can buy time from another node. If a node has time, it can buy money from another node.


