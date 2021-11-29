# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'QLearningAgent', second = 'QLearningAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  a = MyAgent(index = firstIndex)
  b = MyAgent( index = secondIndex)
  return [a, b]


class MyAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
 
  def __init__(self, index = 0, epsilon = .2, training = True, discount = .5, alpha = .2):
    self.index = index
    self.epsilon = epsilon
    self.training = training
    self.weights = util.Counter()
    
    features = ['score', 'numFood', 'height', 'xPos', 'nearestFood']
    for feat in features:
      self.weights[feat] = 1
    

    self.discount = discount
    self.alpha = alpha
    self.observationHistory = []
    self.depthLimit = 4
    

  
  def registerInitialState(self, gameState):
    #super(type(MyAgent)).registerInitialState(gameState)
    self.red = gameState.isOnRedTeam(self.index)
    import distanceCalculator
    self.distancer = distanceCalculator.Distancer(gameState.data.layout)

    # comment this out to forgo maze distance computation and use manhattan distances
    self.distancer.getMazeDistances()
    self.redIndeces = []
    self.blueIndeces = []

    for i in range(4):
      if gameState.isOnRedTeam(i):
        self.redIndeces.append(i)
      else:
        self.blueIndeces.append(i)

    self.origNumRedFood = len(gameState.getRedFood().asList())
    self.origNumBlueFood = len(gameState.getBlueFood().asList())
  
  '''
  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """

    actions = gameState.getLegalActions(self.index)
    return toReturn
    '''


  def chooseAction(self, gameState):
      """
        Returns the minimax action using self.depth and self.evaluationFunction
      """
      "*** YOUR CODE HERE ***"
      toRet = self.alphaBeta(gameState,self.index, depth = 0, alpha = -100000, beta = 100000)
      return toRet


  def alphaBeta (self, gameState, agentIndex = 0, depth = 0, alpha = -100000, beta = 100000):

    
    bestScore = None
    bestAction = None
    worstAction = None
    worstScore = None
    for a in gameState.getLegalActions(agentIndex):
      suc = gameState.generateSuccessor(agentIndex, a)
      if agentIndex in self.blueIndeces:
        val = self.maxValue(suc, agentIndex, depth, alpha, beta)
        if a == "Stop" and len( self.getFood(gameState).asList()) == 1: val -= 10
      else:
        
        val = self.minValue(suc, agentIndex, depth, alpha, beta)
        if a == "Stop" and len (self.getFood(gameState).asList()) == 1: val += 10
      #min = self.minValue(suc, agentIndex, depth, alpha, beta)
      if bestScore is None or val > bestScore:
        bestScore = val
        bestAction = a
      if worstScore is None or val < worstScore:
        worstScore = val
        worstAction = a

    #print bestAction, worstAction, bestScore, worstScore
    return bestAction if agentIndex in self.blueIndeces else worstAction

  def maxValue(self, gameState, agentIndex, depth, alpha, beta):
    #print depth
    if self.depthLimit <= depth:
      toRet = (self.evaluationFunction(gameState, agentIndex))
      return toRet

    bm = None
    bestScore = None
    v = -1000000000

    agentLocs = []
    for i in range (4): 
      agentLocs.append(gameState.getAgentPosition(i))

    locationOfThisGuy = agentLocs[agentIndex]
    if locationOfThisGuy is None:
      import random
      return self.evaluationFunction(gameState, agentIndex)
    #print ("HJERER")



    for move in gameState.getLegalActions(agentIndex):
        suc = gameState.generateSuccessor(agentIndex, move)
        
        if self.index == 3:
          nextIndex = 0
        else:
          nextIndex = self.index+1
        score = self.minValue(suc, nextIndex , depth +1, alpha, beta)
        # if move == "Stop":
        #   score -= 10000
        v = max(v, score)
        if v > beta:
          return (v)
        if (v > alpha):
          alpha = v
          bm = move
          bestScore = v
        #print v
    #print v
    return (v)


  def minValue(self, gameState, agentIndex, depth, alpha, beta):
    if self.depthLimit <= depth:
      return (self.evaluationFunction(gameState, agentIndex))

    bm = None
    v = 100000000

    agentLocs = []
    for i in range (4): 
      agentLocs.append(gameState.getAgentPosition(i))
    #print agentLocs
    locationOfThisGuy = agentLocs[agentIndex]
    if locationOfThisGuy is None:
      import random
      return self.evaluationFunction(gameState, agentIndex)
    #print v, "1"
    #print agentLocs[agentIndex]
    for move in gameState.getLegalActions(agentIndex):
        suc = gameState.generateSuccessor(agentIndex, move)

        if self.index == 3:
          nextIndex = 0
        else:
          nextIndex = self.index+1

        score = self.maxValue(suc,  nextIndex ,depth + 1, alpha, beta)
        #print score, agentIndex
        # print score, "score"
        # print v, "2"
        # if move == "Stop":
        #   score += 10000
        v = min(v, score)

        # print ("HERE", v)
        # print v, "2.5"
        if v < alpha:
          return (v)
        if (v < beta):
          beta = v
          bm = move
        # print v, "3"

    return (v)


  def evaluationFunction(self, gameState, index):
    """
    Returns a counter of features for the state
    """


    myFood = self.getFood(gameState).asList()
    myPos = gameState.getAgentState(self.index).getPosition()
    minDistance = min([self.getMazeDistance(myPos, food) for food in myFood]+[10000])
    toRet = -1*minDistance + len(myFood) * -1000
    #print myFood, gameState.isOnRedTeam(self.index)
    #print toRet, gameState.isOnRedTeam(self.index)

    distancesToGhosts = []
    
    
    if len(myFood) == 0:
      toRet = 1000000
    if gameState.isOnRedTeam(self.index):
      toRet *= -1
    return toRet
  