import numpy as np
import matplotlib.pyplot as plt
import TempSim
import time
import networkx as nx
#%matplotlib qt

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

def InitializePopulation(nCities, populationSize):
    population = np.random.rand(populationSize, nCities)
    return population

def InitializePopulationDynamic(nCities, populationSize):
    population = np.random.rand(populationSize,nCities,nCities)
    return population

'''
def DecodePopulation(nVois, population, zeroThreshold):
    nCities = np.size(population, 1)

    populationCopy = np.zeros((np.size(population, 0), np.size(population, 1)))
    populationCopy[:, :] = population[:, :]
    
    populationCopy[populationCopy < zeroThreshold] = 0

    decodedPopulation = np.floor(
        population/(np.tile(np.sum(population, 1), (nCities, 1))).T*nVois)

    ### FIX ###
    for i in range(populationSize):
        nVoisInCity = np.sum(decodedPopulation, 1)[i]
        while int(nVoisInCity) != int(nVois):
            decodedPopulation[i, np.random.randint(
                0, nCities)] += np.sign(nVois-nVoisInCity)
            decodedPopulation = np.maximum(decodedPopulation, 0)
            nVoisInCity = np.sum(decodedPopulation, 1)[i]

    return decodedPopulation
'''

def DecodePopulationNew(nVois, population, zeroThreshold):
    nCities = np.size(population, 1)

    populationCopy = np.zeros((np.size(population, 0), np.size(population, 1)))
    populationCopy[:, :] = population[:, :]
    
    populationCopy[populationCopy < zeroThreshold] = 0

    normedPopulation = population/(np.tile(np.sum(population, 1), (nCities, 1))).T*nVois
    decodedPopulationMissing = np.floor(population/(np.tile(np.sum(population, 1), (nCities, 1))).T*nVois)
    
    populationLeftSorted = np.argsort(-(normedPopulation - decodedPopulationMissing))
    
    for iChromosome in range(populationSize):
        nVoisInCity = np.sum(decodedPopulationMissing, 1)[iChromosome]
        nMissing = int(nVois - nVoisInCity)    
        decodedPopulationMissing[iChromosome,populationLeftSorted[iChromosome,0:nMissing]] += 1
    decodedPopulation = decodedPopulationMissing

    return decodedPopulation

def DecodePopulationDynamic(nVoisToMove,population,cityMap,voiPositions):
    nNodes = np.size(population,1)
    nChromosomes = np.size(population,0)
    
    cityMapCopy = np.zeros((nNodes,nNodes))
    cityMapCopy[:,:] = cityMap[:,:]
    np.fill_diagonal(cityMapCopy,1)
    cityMapBinary = np.tile(np.heaviside(cityMapCopy,0),(populationSize,1,1))
    
    populationEdges = population*cityMapBinary
    
    moveMatrix = populationEdges - np.transpose(populationEdges,(0, 2, 1))
    for iChromosome in range(nChromosomes):
        diagonal = np.diag(np.diag(populationEdges[iChromosome,:,:]))
        moveMatrix[iChromosome,:,:] = moveMatrix[iChromosome,:,:] + diagonal
    
    moveMatrix = np.triu(moveMatrix)*np.tile(voiPositions.T,(populationSize,nNodes,1))
    return moveMatrix


def FitnessOfPopulation(decodedPopulation, nCities, nAgents, cityMap, cityPositions, nRepetitions, agents, nGroups,mutationProbabilityAgents,endNodeProbabilities):
    nIndividuals = np.size(decodedPopulation, 0)
    populationFitness = np.zeros(nIndividuals)
    maxPopulationFitness = np.zeros(nIndividuals)
    
    for vv in range(nIndividuals):
        for iRepetition in range(nRepetitions):
            tempFitness, tempMaxPopulation, newVoiPositions, nodeUsage = TempSim.runSimulation(decodedPopulation[vv, :], nCities, nAgents, cityMap, cityPositions, agents, nGroups, mutationProbabilityAgents,endNodeProbabilities)
        
        populationFitness[vv] += tempFitness/nRepetitions
        maxPopulationFitness[vv] += tempMaxPopulation/nRepetitions
    return populationFitness, maxPopulationFitness


def TournamentSelection(populationFitness, tournamentSize, tournamentProbability):
    populationSize = np.size(populationFitness, 0)
    tournamentIndeces = np.random.randint(0, populationSize, tournamentSize)
    #tournamentFitness = np.sort(-populationFitness[tournamentIndeces])
    sortingIndeces = np.argsort(-populationFitness[tournamentIndeces])

    probabilities = np.heaviside(-(np.random.rand(tournamentSize) -
                                   tournamentProbability), 0)
    probabilities[tournamentSize-1] = 1
    possibleIndeces = np.nonzero(probabilities)
    chosenIndex = tournamentIndeces[sortingIndeces[possibleIndeces[0][0]]]
    return chosenIndex


def Crossover(chromosome1, chromosome2):
    chromosomeLength = len(chromosome1)
    crossoverPoint = np.random.randint(0, chromosomeLength)

    chromosome1New = np.concatenate(
        (chromosome1[0:crossoverPoint], chromosome2[crossoverPoint:chromosomeLength]))
    chromosome2New = np.concatenate(
        (chromosome2[0:crossoverPoint], chromosome1[crossoverPoint:chromosomeLength]))
    return chromosome1New, chromosome2New


def Mutation(chromosome, mutationProbability, creepRate):
    indecesToMutate = np.nonzero(
        np.heaviside(-(np.random.rand(len(chromosome)) - mutationProbability), 0))[0]

    for iGene in range(len(indecesToMutate)):
        currentGene = chromosome[iGene]
        mutatedGene = currentGene - creepRate/2 + creepRate*np.random.rand()
        mutatedGene = min(max(0, mutatedGene), 1)
        chromosome[iGene] = mutatedGene

    return chromosome


def PlotFitness(noTimeSteps,greatestFitness):
    plt.figure()
    plt.plot(np.linspace(0, noTimeSteps, noTimeSteps), greatestFitness[1:len(greatestFitness)], 'k')

    fontSize = 20
    plt.xlabel('Time', fontsize=fontSize)
    plt.ylabel('Greatest fitness', fontsize=fontSize)
    plt.tick_params(axis='both', labelsize=fontSize)
    plt.title('Greatest fitness of population',fontsize=fontSize)
    plt.show()
    
def PlotGraphAndVois(cityMap,nCities,voiPositions,cityPositions):
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
        labels[i] = int(voiPositions[i])
    nx.draw(G, poss, labels=labels)
    plt.title('Optimal scooter positions',fontsize=fontSize)
    

plt.close("all")
startTime = time.time()

#Load city data
#data_set = np.load('MapToUse4.npz')
data_set = np.load('TestOXMap.npz')
cityMap = data_set['cityMap']
cityPositions = data_set['cityPositions']
#uniformAgents = data_set['uniformAgents']
distributedAgents = data_set['distributedAgents']
nCities = np.size(cityMap,0)

#Model parameters
nAgents = 200
nVoisPerNode = 1
nVois = nCities*nVoisPerNode

#Simulation parameters
mutationProbabilityAgents = 0
nGroups = int(nAgents)

#GA parameters
nGenerations = 300
nRepetitions = 1
populationSize = 30
tournamentSize = 2
tournamentProbability = 0.7
mutationProbability = 3/nCities
crossoverProbability = 0.7
creepRate = 0.2
elitismNumber = 1
zeroThreshold = 0
bestPositionsSaveName = str(nAgents) + '_' + str(nVoisPerNode) + '_' + str(nGenerations) + '_Campus'
#bestPositionsSaveName = '100_1_0_nAgents'

#Initialize agents
agents = np.zeros((nAgents,3),int)
#agents[0:nAgents,:] = uniformAgents[0:nAgents,:]
agents[0:nAgents,:] = distributedAgents[0:nAgents,:]

#Compute the graphs center
networkCenter = FindGraphCenter(cityPositions)
centerDistances = FindDistancesToCenter(cityPositions,networkCenter)
endNodeProbabilities = GetEndNodeProbability(centerDistances)

#Initialize GA population
population = InitializePopulation(nCities, populationSize)

'''
nVoisToMove = 2
voiPositions = np.ones(nCities)
population = InitializePopulationDynamic(nCities, populationSize)
moveMatrix = DecodePopulationDynamic(nVoisToMove,population,cityMap,voiPositions)
'''

greatestFitness = np.zeros(nGenerations+1)

#Run GA
for iTime in range(nGenerations):
    if np.mod(iTime+1, nGenerations/10) == 0:
        print('Progress: ' + str((iTime+1)/nGenerations*100) + ' %')
    
    #Decode population to voi positions and run through simulation
    decodedPopulation = DecodePopulationNew(nVois, population, zeroThreshold)
    populationFitness, maxPopulationFitness = FitnessOfPopulation(
        decodedPopulation, nCities, nAgents, cityMap, cityPositions,nRepetitions, agents, nGroups, mutationProbabilityAgents,endNodeProbabilities)
    
    #Save data of greatest chromosome
    populationFitness = np.divide(populationFitness,maxPopulationFitness)
    generationGreatestFitness = np.max(populationFitness)
    if generationGreatestFitness > greatestFitness[iTime]:
        greatestFitness[iTime+1] = generationGreatestFitness
        bestChromosome = population[np.argmax(populationFitness), :]
        bestDecodedChromosome = decodedPopulation[np.argmax(populationFitness), :]
    else:
        greatestFitness[iTime+1] = greatestFitness[iTime]
    
    #Generate new population
    newPopulation = np.zeros((populationSize, nCities))
    for jChromosomePair in range(int(populationSize/2)):
        #Tournament selection
        chosenIndex1 = TournamentSelection(
            populationFitness, tournamentSize, tournamentProbability)
        chosenIndex2 = TournamentSelection(
            populationFitness, tournamentSize, tournamentProbability)
        chromosome1 = population[chosenIndex1, :]
        chromosome2 = population[chosenIndex2, :]
        
        #Crossover
        rCrossover = np.random.rand()
        if rCrossover < crossoverProbability:
            chromosome1, chromosome2 = Crossover(chromosome1, chromosome2)

        #Mutations
        chromosome1 = Mutation(chromosome1, mutationProbability, creepRate)
        chromosome2 = Mutation(chromosome2, mutationProbability, creepRate)
        
        newPopulation[2*jChromosomePair, :] = chromosome1
        newPopulation[2*jChromosomePair+1, :] = chromosome2
    
    #Elitism
    newPopulation[0:elitismNumber, :] = bestChromosome
    population = newPopulation
    
endTime = time.time()
runTime = endTime - startTime
print('Runtime: ' + str(runTime) + ' s')

np.savez(bestPositionsSaveName, bestPositions = np.array(bestDecodedChromosome),greatestFitness = np.array(greatestFitness),nGenerations = np.array(nGenerations))

#Plots
PlotFitness(nGenerations, greatestFitness)
PlotGraphAndVois(cityMap,nCities,decodedPopulation[0,:],cityPositions)
plt.show()