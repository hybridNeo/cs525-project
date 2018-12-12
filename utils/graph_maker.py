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
        num_dep = int(randint(2, numTasks-i) * factor)
        for j in range(1,num_dep):
            dep = i+j
            adjMatrix[i][dep] = 1
            adjMatrix[dep][i] = -1
    for i in range(numTasks-1):
        found = False
        for j in range(numTasks-2):
            if adjMatrix[i][j] == 1:
                found = True
        if not found:
            adjMatrix[i][numTasks-1] = 1
            adjMatrix[numTasks-1][i] = -1

    compute_cost = [[randint(costLow, costHigh) for i in range(3)] for j in range(numTasks)]
    print_graph(adjMatrix)
    #tGraph = taskGraph(adjMatrix, entryNode, exitNode, numTasks)
    return adjMatrix, entryNode, exitNode, numTasks, numProcs, compute_cost

def fft_graph():
    '''
        FFT DAG from the paper
    '''

    adjMatrix = [
            [0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [-1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0],
            [-1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0],
            [0,-1,0,0,0,0,0,1,1,0,0,0,0,0,0,0],
            [0,-1,0,0,0,0,0,1,1,0,0,0,0,0,0,0],
            [0,0,-1,0,0,0,0,0,0,1,1,0,0,0,0,0],
            [0,0,-1,0,0,0,0,0,0,1,1,0,0,0,0,0],
            [0,0,0,-1,-1,0,0,0,0,0,0,1,0,1,0,0],
            [0,0,0,-1,-1,0,0,0,0,0,0,0,1,0,1,0],
            [0,0,0,0,0,-1,-1,0,0,0,0,1,0,1,0,0],
            [0,0,0,0,0,-1,-1,0,0,0,0,0,1,0,0,1],
            [0,0,0,0,0,0,0,-1,0,-1,0,0,0,0,0,1],
            [0,0,0,0,0,0,0,0,-1,0,-1,0,0,0,0,1],
            [0,0,0,0,0,0,0,-1,0,-1,0,0,0,0,0,1],
            [0,0,0,0,0,0,0,0,-1,0,-1,0,0,0,0,1],
            [0,0,0,0,0,0,0,0,0,0,0,-1,-1,-1,-1,0]
            ]
    entryNode = 0
    exitNode = 15
    numTasks = 16
    numProcs = 3
    print_graph(adjMatrix)
    # tGraph = taskGraph(adjMatrix, entryNode, exitNode, numTasks)

    computeCost = [[14,16,9],[14,16,9],[13,19,18],[11,13,19],[13,8,17],[12,13,10],[13,16,9],[7,15,11],[5,11,14],[18,12,20],[21,7,16], [13,16,9],[7,15,11],[5,11,14],[18,12,20],[21,7,16]]
    return adjMatrix, entryNode, exitNode, numTasks, numProcs, computeCost

def mpeg_graph():
    """
     Mpeg graph
    """
    adjMatrix = [
            [0,1,1,1,1,0,0,0,0,0,0,0,0,0],
            [-1,0,0,0,0,1,0,0,0,0,0,0,0,0],
            [-1,0,0,0,0,1,0,0,0,0,0,0,0,0],
            [-1,0,0,0,0,0,1,1,0,0,0,0,0,0],
            [-1,0,0,0,0,0,0,0,1,0,0,0,0,0],
            [0,-1,-1,0,0,0,-1,-1,0,1,1,1,0,0],
            [0,0,0,-1,0,1,0,0,0,0,0,0,0,0],
            [0,0,0,-1,0,1,0,0,0,0,0,0,0,0],
            [0,0,0,0,-1,0,0,0,0,0,1,1,1,0],
            [0,0,0,0,0,-1,0,0,0,0,0,0,0,1],
            [0,0,0,0,0,-1,0,0,-1,0,0,0,0,1],
            [0,0,0,0,0,-1,0,0,-1,0,0,0,0,1],
            [0,0,0,0,0,0,0,0,-1,0,0,0,0,1],
            [0,0,0,0,0,0,0,0,0,-1,-1,-1,-1,0]
            ]
    entryNode = 0
    exitNode = 13
    numTasks = 14
    numProcs = 3
    print_graph(adjMatrix)
    computeCost = [[14,16,9],[13,19,18],[11,13,19],[13,8,17],[12,13,10],[13,16,9],[7,15,11],[5,11,14],[18,12,20],[21,7,16], [13,16,9],[7,15,11],[5,11,14],[18,12,20]]

    return adjMatrix, entryNode, exitNode, numTasks, numProcs, computeCost

def gauss_graph():
    """
      gauss graph
    """

    adjMatrix = [
            [0,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
            [-1,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
            [-1,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
            [-1,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
            [-1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [0,-1,0,0,0,0,1,0,1,0,0,0,0,0,0],
            [0,0,0,0,0,-1,0,1,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,-1,0,0,0,1,0,1,0,0],
            [0,0,-1,-1,0,-1,0,0,0,0,1,0,0,0,0],
            [0,0,0,0,0,-1,0,0,0,0,0,0,0,0,1],
            [0,0,0,0,0,0,0,-1,-1,0,0,1,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,-1,0,1,0],
            [0,0,0,0,0,0,0,-1,0,0,0,0,0,0,1],
            [0,0,0,0,0,-1,0,0,0,0,0,0,0,0,1]
            [0,0,0,0,-1,0,0,0,0,-1,0,0,-1,-1,0]
            ]

    entryNode = 0
    exitNode = 15
    numTasks = 16
    numProcs = 3
    print_graph(adjMatrix)
    # tGraph = taskGraph(adjMatrix, entryNode, exitNode, numTasks)

    computeCost = [[14,16,9],[14,16,9],[13,19,18],[11,13,19],[13,8,17],[12,13,10],[13,16,9],[7,15,11],[5,11,14],[18,12,20],[21,7,16], [13,16,9],[7,15,11],[5,11,14],[18,12,20],[21,7,16]]

    return adjMatrix, entryNode, exitNode, numTasks, numProcs, computeCost

if __name__ == '__main__':
    generate_random_dag(15,3,0.2)

