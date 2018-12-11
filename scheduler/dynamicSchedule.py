"""
    This is the top level file for dynamic scheduling

    We make the following assumptions:
        1. The communication cost is uniform (read from shared memory) and is incl in compute cost.
        2. The Estimated Finish Time is the actual finish time (ideal system).

    The schedule requires a DAG as input.
"""
import numpy as np
from est import est
from uprank import upRank
from est import getPredecessors
from collections import OrderedDict
from staticSchedule import staticSchedule

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

def dynamicSchedule(taskScheduled, updatedCost, computeCost):

    # Update compute costs
    computeCost= updateCost(updatedCost, computeCost)

    # Rerun the rank calculation
    uRank = [None] * tGraph.numTasks
    uRank, _ = upRank(tGraph, computeCost, tGraph.entryNode, uRank)
    scheduleOrder = list(np.argsort(uRank)[::-1])

    # Delete the tasks that already have been scheduled/completed
    for c in taskScheduled.keys():
        scheduleOrder.remove(c)

    # Updated dict for the final schedule
    taskSchedule = dict(taskScheduled)

    # In the order of schedule, find the best processor to put the task on.
    # This is based on the EST estimation.
    for node in scheduleOrder:
        # Get the EST for all the procs that can evaluate this task.
        allProcs = [proc for proc,cost in enumerate(computeCost[node]) if cost != INF]

        estProcs = []
        # Check which proc has the min EST
        for proc in allProcs:
            tEst,tEft = est(tGraph, computeCost, taskSchedule, node, proc)
            estProcs.append([tEst,tEft])

        # Find the min EST
        EST = list(zip(*estProcs))[1]
        minESTIdx = min(range(len(EST)), key=EST.__getitem__)

        # print("For node %d we have ESTs returned as " % node, estProcs, " and min EST is for %d proc" % minESTIdx)

        #Update the schedule - [node, EST, EFT, proc]
        taskSchedule[node] = {'time': (estProcs[minESTIdx][0], estProcs[minESTIdx][1]),
                                    'predecessors': getPredecessors(tGraph, node), 'proc': minESTIdx}

        # print("Added the task schedule", taskSchedule[node])

    # Create an ordered Dictionary
    orderedSchedule = [(key, taskSchedule[key]) for key in scheduleOrder]

    return OrderedDict(orderedSchedule)

def updateCost(updatedCost, computeCost):
    """
        This function updates the cost to new ones.
    """

    for cost in updatedCost:
        node, proc, val = cost
        computeCost[node][proc] = val

    return computeCost

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

    taskSchedule = staticSchedule(tGraph, computeCost)

    print("Old Schedule", taskSchedule)

    # Assume some of them got scheduled with new cost values.
    taskScheduled = {0:{'proc': 2, 'predecessors': [], 'time': (0, 15)},
                     1: {'proc': 0, 'predecessors': [0], 'time': (15, 32)}}
    updatedCost = [(0,2,15),(1,0,17)]

    newSchedule = dynamicSchedule(taskScheduled, updatedCost, computeCost)

    print("New Schedule", newSchedule)
