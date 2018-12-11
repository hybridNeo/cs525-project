import sys
from random import randint

sys.path.insert(0,'../scheduler/')
from staticSchedule import taskGraph

def print_graph(graph):
    for i in graph:
        print(i)

def generate_random_dag(numTasks, numProcs, factor):
    '''
        e.g
        set factor as 1 for heavy workload
        set factor as 0.5 for mild workload

    '''
    costHigh = int(17*factor)
    costLow = int(10*factor)
    entryNode = 0
    exitNode = numTasks-1
    adjMatrix =[[0 for i in range(numTasks)] for j in range(numTasks)]

    for i in range(numTasks-1):
        num_dep = int(randint(1, numTasks-1-i) * factor)
        for j in range(num_dep):
            dep = randint(i+1,numTasks-1)
            adjMatrix[i][dep] = 1
            adjMatrix[dep][i] = -1
    compute_cost = [[randint(costLow, costHigh) for i in range(3)] for j in range(numTasks)]
    tGraph = taskGraph(adjMatrix, entryNode, exitNode, numTasks)
    return tGraph, compute_cost

def fft_graph():
    '''
        FFT DAG from the paper
    '''

    adjMatrix = [
            [0,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
            [-1,0,0,1,1,0,0,0,0,0,0,0,0,0,0],
            [-1,0,0,0,0,1,1,0,0,0,0,0,0,0,0],
            [0,-1,0,0,0,0,0,1,1,0,0,0,0,0,0],
            [0,-1,0,0,0,0,0,1,1,0,0,0,0,0,0],
            [0,0,-1,0,0,0,0,0,0,1,1,0,0,0,0],
            [0,0,-1,0,0,0,0,0,0,1,1,0,0,0,0],
            [0,0,0,-1,-1,0,0,0,0,0,0,1,0,1,0],
            [0,0,0,-1,-1,0,0,0,0,0,0,0,1,0,1],
            [0,0,0,0,0,-1,-1,0,0,0,0,1,0,1,0],
            [0,0,0,0,0,-1,-1,0,0,0,0,0,1,0,1],
            [0,0,0,0,0,0,0,-1,0,-1,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,-1,0,-1,0,0,0,0],
            [0,0,0,0,0,0,0,-1,0,-1,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,-1,0,-1,0,0,0,0],]
    entryNode = 0
    exitNode = 14
    numTasks = 15
    numProcs = 3
    print_graph(adjMatrix)
    tGraph = taskGraph(adjMatrix, entryNode, exitNode, numTasks)

    computeCost = [[14,16,9],[13,19,18],[11,13,19],[13,8,17],[12,13,10],[13,16,9],[7,15,11],[5,11,14],[18,12,20],[21,7,16], [13,16,9],[7,15,11],[5,11,14],[18,12,20],[21,7,16]]
    return tGraph, computeCost

if __name__ == '__main__':
    generate_random_dag(15,3,0.2)

