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
    self.depthLimit = 5
    

  
  def registerInitialState(self, gameState):
    #super(type(MyAgent)).registerInitialState(gameState)
    self.red = gameState.isOnRedTeam(self.index)
    import distanceCalculator
    self.distancer = distanceCalculator.Distancer(gameState.data.layout)

    # comment this out to forgo maze distance computation and use manhattan distances
    self.distancer.getMazeDistances()
    self.redIndeces = []
    self.blueIndeces = []

    for i in range(3):
      if gameState.isOnRedTeam(i):
        self.redIndeces.append(i)
      else:
        self.blueIndeces.append(i)
  
  '''
  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """

    actions = gameState.getLegalActions(self.index)
    return toReturn
    '''

  def min(gameState, index):
    #min is the other team. In here, we'll need to reason over uncertainty
    pass

  def max(gameState, index):
    #max is just our team. our eval function will need to be generic
    pass

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
      max = self.maxValue(suc, agentIndex, depth, alpha, beta)
      min = self.minValue(suc, agentIndex, depth, alpha, beta)
      if bestScore is None or max > bestScore:
        bestScore = max
        bestAction = a
      if worstScore is None or min < worstScore:
        worstScore = min
        worstAction = a

    print bestAction, worstAction, bestScore, worstScore
    return bestAction if agentIndex in self.blueIndeces else worstAction

  def maxValue(self, gameState, agentIndex, depth, alpha, beta):
    #print depth
    if self.depthLimit <= depth:
      toRet = (self.evaluationFunction(gameState))
      print "HEREafsd", toRet
      return toRet

    bm = None
    bestScore = None
    v = -10000000

    agentLocs = []
    for i in range (4): 
      agentLocs.append(gameState.getAgentPosition(i))

    locationOfThisGuy = agentLocs[agentIndex]
    if locationOfThisGuy is None:
      import random
      return (random.randint(1,15))
    #print ("HJERER")



    for move in gameState.getLegalActions(agentIndex):
        suc = gameState.generateSuccessor(agentIndex, move)
        
        if self.index == 3:
          nextIndex = 0
        else:
          nextIndex = self.index+1
        score = self.minValue(suc, nextIndex , depth +1, alpha, beta)
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
      return (self.evaluationFunction(gameState))

    bm = None
    v = 10000000

    agentLocs = []
    for i in range (4): 
      agentLocs.append(gameState.getAgentPosition(i))
    #print agentLocs
    locationOfThisGuy = agentLocs[agentIndex]
    if locationOfThisGuy is None:
      return(0)
      noisyDist = gameState.getAgentDistances()[agentIndex]
      probs = []
      for i in range(noisyDist-6, noisyDist+6):
        probs.append(gameState.getDistanceProb(i, noisyDist))
      print probs

    #print v, "1"
    for move in gameState.getLegalActions(agentIndex):
        suc = gameState.generateSuccessor(agentIndex, move)

        if self.index == 3:
          nextIndex = 0
        else:
          nextIndex = self.index+1

        score = self.maxValue(suc,  nextIndex ,depth + 1, alpha, beta)
        # print score, "score"
        # print v, "2"
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


  def evaluationFunction(self, gameState):
    """
    Returns a counter of features for the state
    """
    #pacman position
    #getScore()
    #getCapsules returns list of positions
    #getNumFood()
    #getFood()


    #IMPORTANT: Need to generalize for both colors. Make it our food, their food

    IAmBlue = not gameState.isOnRedTeam(self.index)

    features = util.Counter()
    features['score'] = gameState.getScore()
    features['numFood'] = len(gameState.getRedFood().asList())
    features['height'] = gameState.getAgentPosition(self.index)[1] 
    features['xPos'] = gameState.getAgentPosition(self.index)[0]
    loc = gameState.getBlueFood().asList()[0]
    #print loc, gameState.getAgentPosition(self.index)
    features['nearestFood'] = self.getMazeDistance(loc, gameState.getAgentPosition(self.index))


    indecesOfMyTeam = []
    indecesOfOtherTeam = []

    for i in range(3):
      if IAmBlue and gameState.isOnRedTeam(i):
        indecesOfOtherTeam.append(i)
      else:
        indecesOfMyTeam.append(i)


    distances = gameState.getAgentDistances()

    #prob = gameState.getDistanceProb() #takes true, noisy


    #print distances, self.index

    agentLocs = []
    for i in range (3): 
      agentLocs.append(gameState.getAgentPosition(i))

    #print agentLocs
    '''
    self.blueIndeces = gameState.getBlueTeamIndices()
    self.redIndeces = gameState.getRedTeamIndices()

    '''
    eval = - gameState.getAgentPosition(self.index)[1] 
    print eval
    return -55
  