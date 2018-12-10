"""
    Implement a logic to calculate the estimated start time.

    Inputs:
        - tGraph: (V,E) graph, that has a 1 for connections.
        - computeCost: VxQ matrix, every task v is assigned a cost for Q processors.
        - taskSchedule - Already scheduled tasks (note that all predecessors mucst already be scheduled.
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


def est(tGraph, computeCost, taskSchedule, node, proc):
    """
        Calculate the estiamted start time.
    """

    # print("Getting the EST for node %d for proc %d" % (node, proc))

    if(node == tGraph.entryNode):
        # This is the entry node, can start immediately.

        return 0,computeCost[node][proc]

    else:
        # Get the successors and run through them.
        pred = getPredecessors(tGraph, node)

        # Actual finish times
        p_aft = []

        # Run through all of them and get their AFT
        for p in pred:
            if(p not in taskSchedule.keys()):
                sys.exit("Error, all predecessors are not scheduled." + str(p))
            p_aft.append(taskSchedule[p][2])

        aft = max(p_aft)

        # Run through the processor and find its availability
        avail = getAvail(taskSchedule, proc)

        # Now whichever is the maximum, that is the estimated start time.
        myEST = max(avail, aft)

        # Whatever is the compute cost of the node tells the estimated finish time.
        myEFT = myEST + computeCost[node][proc]

        return myEST, myEFT


def getPredecessors(tGraph, node):
    """
        Returns all the predecessors of the node.
    """
    # Retrive the adjacency mat
    adj = tGraph.adjMatrix[node]

    # All the -1s represent a predecessor
    return [idx for idx,val in enumerate(adj) if val == -1]

def getAvail(taskSchedule, proc):
    """
        return the next availability of the given proc
    """
    # Retrieve all the nodes that are expected to run on this proc.
    allTasks = [sched[2] for sched in taskSchedule.values() if  sched[3]==proc]

    # return the max eft
    return max(allTasks) if allTasks else 0


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

    entryNode = 0
    exitNode = 9
    numTasks = 10
    numProcs = 3

    tGraph = taskGraph(adjMatrix, entryNode, exitNode, numTasks)

    computeCost = [[14,16,9],[13,19,18],[11,13,19],[13,8,17],[12,13,10],
                        [13,16,9],[7,15,11],[5,11,14],[18,12,20],[21,7,16]]

    taskSchedule = {}

    for i in range(numTasks):
        pCost = []
        for p in range(numProcs):
            tEst,tEft = est(tGraph, computeCost, taskSchedule, i, p)
            pCost.append([tEst,tEft])
        # Whichever has the minimum est, update task schedule
        c = zip(*pCost)[0]
        minIdx = min(xrange(len(c)), key=c.__getitem__)

        taskSchedule[i] = [i, pCost[minIdx][0],pCost[minIdx][1], minIdx]

    print(taskSchedule)


