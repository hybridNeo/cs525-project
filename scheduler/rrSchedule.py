"""
    Round robin scheduler.

    The schedule requires a DAG as input.
"""
import numpy as np
from est import getPredecessors
from collections import OrderedDict

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

def rrSchedule(tGraph, computeCost):
    """
        Main function.
    """
    numProcs = len(computeCost[0])
    scheduleOrder = range(tGraph.numTasks)

    taskSchedule = {}
    proc = []

    for node in scheduleOrder:
        if(proc == []):
            proc = range(numProcs)
        proc, nextProc = getNextProc(computeCost, node, proc)
        taskSchedule[node] = {'time': [0, computeCost[node][nextProc]], 'predecessors': getPredecessors(tGraph,node), 'proc': nextProc}

    # Create an ordered Dictionary
    orderedSchedule = [(key, taskSchedule[key]) for key in scheduleOrder]

    return OrderedDict(orderedSchedule)

def getNextProc(computeCost, node, procAvail):
    """
        Make sure the returned one doesn't have INF
    """
    # Get the EST for all the procs that can evaluate this task.
    allProcs = [proc for proc,cost in enumerate(computeCost[node]) if cost != INF]

    for proc in allProcs:
        if(proc in procAvail):
            procAvail.remove(proc)
            return procAvail, proc

    # if you didn't find any, then dump the current list and create a new one.
    numProcs = len(computeCost[0])
    procAvail = range(numProcs)
    procAvail.remove(allProcs[0])

    return procAvail, allProcs[0]

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

    taskSchedule = rrSchedule(tGraph, computeCost)

    print(taskSchedule)
