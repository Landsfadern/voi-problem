import numpy as np
import matplotlib.pyplot as plt
import TempSim
import networkx as nx
#%matplotlib qt

def FitnessOfPopulation(voiPositions, nCities, nAgents, cityMap, cityPositions,agents, nGroups, mutationProbabilityAgents,endNodeProbabilities):
    fitness, maxFitness, newVoiPositions, nodeUsage = TempSim.runSimulation(voiPositions, nCities, nAgents, cityMap, cityPositions, agents, nGroups, mutationProbabilityAgents,endNodeProbabilities)
    return fitness, maxFitness, newVoiPositions, nodeUsage

'''
def initAgents(nAgents, nNodes):
    agents = np.zeros((nAgents, 3), dtype=np.int8)
    for i in range(nAgents):
        cityIndexes = [x for x in range(nNodes)]
        startCity = np.random.choice(cityIndexes, 1)
        currentCity = startCity
        cityIndexes.remove(startCity)
        endCity = np.random.choice(cityIndexes, 1)
        agents[i, 0] = currentCity
        agents[i, 1] = startCity
        agents[i, 2] = endCity
    return agents
'''

def FindDistancesToCenter(cityPositions,networkCenter):
    xValues = cityPositions[:,0] - networkCenter[0]
    yValues = cityPositions[:,1] - networkCenter[1]
    centerDistances = np.sqrt(
        np.power(xValues,2) + np.power(yValues,2))
    return centerDistances

def GetEndNodeProbability(centerDistances):
    inverseDistance = 1/centerDistances
    totalInverseDistance = sum(inverseDistance)
    endNodeProbability = inverseDistance/totalInverseDistance
    return endNodeProbability

def FindGraphCenter(nodePositions):
    networkCenter = np.sum(nodePositions,0)/np.size(nodePositions,0)
    return networkCenter

def VoiDistanceFromCenter(nodePositions,voiPositions,networkCenter):
    voiDistanceFromCenter = np.matmul(voiPositions,np.sqrt(np.sum((nodePositions-networkCenter)**2,1)))/np.sum(voiPositions)
    return voiDistanceFromCenter

def PlotGraphAndIndices(cityMap,nCities,voiPositions,cityPositions):
    fontSize = 20
    plt.figure()
    G = nx.from_numpy_matrix(cityMap)
    indices = {}
    poss = {}
    for i in range(nCities):
        poss[i] = cityPositions[i]
        indices[i] = i
    labels = {}
    for i in range(nCities):
        labels[i] = voiPositions[i]
    #nx.draw_networkx(G,poss)
    nx.draw(G, poss, labels=indices)
    plt.title('Network with node indeces',fontsize=fontSize)
    plt.gca().set_aspect('equal', adjustable='box')
    
def PlotFitness(fitness,maxFitness):
    fontSize = 40
    lineWidth = 4
    
    plt.figure()
    plt.plot(maxFitness,'k',linewidth = lineWidth)
    plt.plot(fitness,'r',linewidth = lineWidth)
    
    plt.xlabel('Simulated days',fontsize=fontSize)
    plt.ylabel('Scooter usage',fontsize=fontSize)
    plt.legend(['Maximum usage','Actual usage'],fontsize=fontSize,frameon=False)
    plt.tick_params(axis='both', labelsize=fontSize)
    #plt.title('Scooter usage',fontsize=fontSize)
    
    meanRelativeVoiUsage = np.mean(np.divide(fitness,maxFitness))
    plt.figure()
    plt.plot(np.divide(fitness,maxFitness),'k',linewidth = lineWidth)
    plt.plot(np.ones(len(fitness))*meanRelativeVoiUsage,'--r',linewidth = lineWidth)
    print(meanRelativeVoiUsage)
    
    plt.xlabel('Simulated days',fontsize=fontSize)
    plt.ylabel('Relative scooter usage',fontsize=fontSize)
    plt.tick_params(axis='both', labelsize=fontSize)
    #plt.title('Actual voi usage relative to maximum voi usage',fontsize=fontSize)
    plt.legend(['Relative voi usage','Mean relative voi usage (' + str(np.round(meanRelativeVoiUsage,3)) + ')'],fontsize=fontSize,frameon=False)
    
def PlotVoiDistanceFromCenter(voiDistanceFromCenter):
    fontSize = 60
    lineWidth = 6
    
    plt.figure()
    plt.plot(voiDistanceFromCenter,'k',linewidth = lineWidth)
    
    plt.xlabel('Simulated days',fontsize=fontSize)
    plt.ylabel('Mean distance',fontsize=fontSize)
    plt.tick_params(axis='both', labelsize=fontSize)
    #plt.title('The scooters mean distance from the networks center',fontsize=fontSize)
    
def PlotAgentsStartEndDistribution(agents,nNodes):
    fontSize = 20
    
    plt.figure()
    plt.hist(agents[:,1],nNodes,fc=(0, 0, 1, 0.5))
    plt.hist(agents[:,2],nNodes,fc=(1, 0, 0, 0.5))
    
    plt.xlabel('Node index',fontsize=fontSize)
    plt.ylabel('Number of agents',fontsize=fontSize)
    plt.legend(['Start node','End node'],fontsize=fontSize,frameon=False)
    plt.tick_params(axis='both', labelsize=fontSize)
    plt.title('Distribution of agents start and end',fontsize=fontSize)
    
plt.close("all")

def PlotAverageVoisPerNode(voisPerNode):
    fontSize = 20
    avgVois = np.average(voisPerNode, axis=1)
    plt.figure()
    plt.bar([x for x in range(len(avgVois))],height=avgVois)
    plt.xlabel('Node index',fontsize=fontSize)
    plt.ylabel('Avg. number of vois',fontsize=fontSize)
    plt.title('Average number of vois per node',fontsize=fontSize)
    
def PlotGraphAndVois(cityMap,nCities,voiPositions,cityPositions,nodeSize):
    fontSize = 50
    edgeWidth = 5
    plt.figure()
    G = nx.from_numpy_matrix(cityMap)
    indices = {}
    poss = {}
    for i in range(nCities):
        poss[i] = cityPositions[i]
        indices[i] = i
    labels = {}
    for i in range(nCities):
        labels[i] = int(voiPositions[i])
    #nx.draw(G, poss, labels=labels,node_size = nodeSize,font_size = fontSize,width=edgeWidth)
    nx.draw(G, poss,node_size = nodeSize,font_size = fontSize,width=edgeWidth)
    plt.title('Scooter positions',fontsize=fontSize)
    plt.gca().set_aspect('equal', adjustable='box')
    
def PlotGreatestFitness(nGenerations,greatestFitness):
    plt.figure()
    plt.plot(np.linspace(0, nGenerations, nGenerations), greatestFitness[1:len(greatestFitness)], 'k')

    fontSize = 20
    plt.xlabel('Generations', fontsize=fontSize)
    plt.ylabel('Greatest fitness', fontsize=fontSize)
    plt.tick_params(axis='both', labelsize=fontSize)
    plt.title('Greatest fitness of population',fontsize=fontSize)
    plt.show()

def UpdateLimitedVoiPositions(voiPositions,nodeUsage,noVoisToReposition,optimalVoiPositions):
    nNodes = len(voiPositions)
    
    tooManyVois = np.maximum(voiPositions - optimalVoiPositions,0)
    tooFewVois = np.maximum(optimalVoiPositions - voiPositions,0)
    
    #Add vois to nodes
    weightedSortedNodeUsage = nodeUsage*tooFewVois/sum(nodeUsage*tooFewVois)*noVoisToReposition
    addedVois = np.floor(weightedSortedNodeUsage)
    
    nVoisToPlace = noVoisToReposition - np.sum(addedVois)
    sortingIndeces = np.argsort(weightedSortedNodeUsage - addedVois)
    addedVois[sortingIndeces[int(nNodes-nVoisToPlace):nNodes]] += 1
    
    #Remove vois from nodes
    removedVois = np.zeros(nNodes)
    for i in range(noVoisToReposition):
        nodeToTakeFrom = np.argmax(tooManyVois)
        tooManyVois[nodeToTakeFrom] -= 1
        removedVois[nodeToTakeFrom] +=1
        
    newVoiPositions = voiPositions + addedVois - removedVois
    return newVoiPositions
        

#Import map to use and agents
#data_set = np.load('MaptoUse4.npz')
data_set = np.load('TestOXMap.npz')
cityMap = data_set['cityMap']
cityPositions = data_set['cityPositions']
#uniformAgents = data_set['uniformAgents']
distributedAgents = data_set['distributedAgents']
nCities = np.size(cityMap,0)

#Import optimized voi positions
voiPositionData = np.load('100_1_1_Campus.npz')

#Compute the graphs center
networkCenter = FindGraphCenter(cityPositions)
centerDistances = FindDistancesToCenter(cityPositions,networkCenter)
endNodeProbabilities = GetEndNodeProbability(centerDistances)

#Model parameters
nAgents = 100
nVois = 1*nCities
nTimeSteps = 10
mutationProbabilityAgents = 0
nGroups = int(nAgents)

noVoisToReposition = 0

#Load agents
agents = np.zeros((nAgents,3),int)
#agents[0:nAgents,:] = uniformAgents[0:nAgents,:]
agents[0:nAgents,:] = distributedAgents[0:nAgents,:]

#Initial voi distribution
voiPositions = np.ones(nCities)*nVois/nCities           ### UNIFORM VOI POSITIONS
#voiPositions = voiPositionData['bestPositions']          ### (OPTIMIZED)

fitness = np.zeros(nTimeSteps)
maxFitness = np.zeros(nTimeSteps)
voiDistanceFromCenter = np.zeros(nTimeSteps)
voisPerNode = np.zeros((nCities, nTimeSteps))

for iTime in range(nTimeSteps):
    if np.mod(iTime+1, nTimeSteps/10) == 0:
        print('Progress: ' + str((iTime+1)/nTimeSteps*100) + ' %')
        
    #voiPositions = np.ones(nCities)*nVois/nCities ### RESETS ALL VOI POSITIONS EVERY DAY (UNIFORMLY)
    voiPositions = voiPositionData['bestPositions'] ### RESETS ALL VOI POSITIONS EVERY DAY (OPTIMIZED)
    
    #Run simulation
    fitness[iTime], maxFitness[iTime], newVoiPositions, nodeUsage = FitnessOfPopulation(voiPositions, nCities, nAgents, cityMap, cityPositions,agents, nGroups, mutationProbabilityAgents,endNodeProbabilities)
    
    voisPerNode[:,iTime] = newVoiPositions
    voiDistanceFromCenter[iTime] = VoiDistanceFromCenter(cityPositions,newVoiPositions,networkCenter)

    #newVoiPositions = UpdateLimitedVoiPositions(newVoiPositions,nodeUsage,noVoisToReposition,np.ones(nCities)*nVois/nCities) ### (UNIFORM)
    #newVoiPositions = UpdateLimitedVoiPositions(newVoiPositions,nodeUsage,noVoisToReposition,voiPositionData['bestPositions']) ### (OPTIMIZED)
    voiPositions = newVoiPositions

#Load data for GA fitness plot
nGenerations = voiPositionData['nGenerations']
greatestFitness = voiPositionData['greatestFitness']

#nodeSize = (np.bincount(agents[:,1]) + np.bincount(agents[:,2]))/nAgents*10000

#Plots
#PlotGraphAndIndices(cityMap,nCities,voiPositions,cityPositions)
#PlotAverageVoisPerNode(voisPerNode)
PlotFitness(fitness,maxFitness)
PlotVoiDistanceFromCenter(voiDistanceFromCenter)
#PlotAgentsStartEndDistribution(agents,nCities)
#PlotGraphAndVois(cityMap,nCities,voiPositionData['bestPositions'],cityPositions,nodeSize)
#PlotGraphAndVois(cityMap,nCities,voiPositions,cityPositions,nodeSize)
#PlotGraphAndVois(cityMap,nCities,np.bincount(agents[:,1]) + np.bincount(agents[:,2]),cityPositions,nodeSize)
PlotGreatestFitness(nGenerations, greatestFitness)
plt.show()
