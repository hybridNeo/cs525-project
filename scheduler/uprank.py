"""
    Implement a logic similar to HEFT for scheduling.

    Inputs:
        - tGraph: (V,E) graph, that has a 1 for connections.
        - computeCost: VxQ matrix, every task v is assigned a cost for Q processors.
"""

import os, sys
import numpy as np

INF = float("inf")

class taskGraph():
    """
        This is the input DAG.
    """

    def __init__(self, adjMatrix, entryNode, exitNode, numTasks):
        self.adjMatrix = adjMatrix
        self.entryNode = entryNode
        self.exitNode = exitNode
        self.numTasks = numTasks


def upRank(tGraph, computeCost, node, uRank):
    """
        Recursively calculate the upward ranking.
    """


    if(node == tGraph.exitNode):
        # This is the exit node, return only its cost
        cost = getAvgCost(computeCost,node)
        uRank[node] = cost

        return uRank, cost

    else:
        # If this node was previously visited, return the rank.
        if(uRank[node] != None):
            return uRank, uRank[node]
        else:
            # Get the successors and run through them.
            succ = getSuccessors(tGraph, node)

            s_ranks = []
            # Run through all of them and get their ranks
            for s in succ:
                uRank, s_rank = upRank(tGraph, computeCost, s, uRank)
                s_ranks.append(s_rank)

            # Now calculate the node's rank
            myCost = getAvgCost(computeCost,node) + max(s_ranks)

            # Update the rank and return
            uRank[node] = myCost

            return uRank, myCost


def getSuccessors(tGraph, node):
    """
        Returns all the successors of the node.
    """
    # Retrive the adjacency mat
    adj = tGraph.adjMatrix[node]

    # All the 1s represent a successor
    return [idx for idx,val in enumerate(adj) if val == 1]

def getAvgCost(computeCost, node):
    """
        return the average cost needed to run the task on all the processors.
    """
    # Retrieve allt he procs that can run this task
    allCost = computeCost[node]

    allRunCost = [i for i in allCost if i != INF]

    # return the average
    return sum(allRunCost)/float(len(allRunCost))


if __name__ == '__main__':

    """
        Test the algorithm.
    """
    adjMatrix = [[0,1,1,1,1,1,0,0,0,0],
                 [-1,0,0,0,0,0,0,1,1,0],
                 [-1,0,0,0,0,0,1,0,0,0],
                 [-1,0,0,0,0,0,0,1,1,0],
                 [-1,0,0,0,0,0,0,0,1,0],
                 [-1,0,0,0,0,0,0,1,0,0],
                 [0,0,-1,0,0,0,0,0,0,1],
                 [0,-1,0,-1,0,-1,0,0,0,1],
                 [0,-1,0,-1,-1,0,0,0,0,1],
                 [0,0,0,0,0,0,-1,-1,-1,0]]

    # adjMatrix = [[1,2,3,4,5],[7,8],[6],[7,8],[8],[7],[9],[9],[9]]
    entryNode = 0
    exitNode = 9
    numTasks = 10

    tGraph = taskGraph(adjMatrix, entryNode, exitNode, numTasks)

    computeCost = [[14,16,9],[13,19,18],[11,13,19],[13,8,17],[12,13,10],
                        [13,16,9],[7,15,11],[5,11,14],[18,12,20],[21,7,16]]

    uRank = [None]*numTasks

    print(upRank(tGraph, computeCost, entryNode, uRank))


