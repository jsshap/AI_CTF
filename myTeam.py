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
    
    features = ['FoodLeft', 'FoodToEat']
    for feat in features:
      self.weights[feat] = 1
    

    self.discount = discount
    self.alpha = alpha
    self.observationHistory = []
    


  def readWeights(self):
    try:
      f = open ('weights.txt', 'r')
      lines = f.readLines()
      for l in lines.split(","):
        self.weights[l[0]] = float(l[1])
    except:
      pass
    print self.weights, "START"

  def writeWeights(self):
    f = open("weights", "w")
    for w in self.weights:
      f.write(w + "," + str(self.weights[w])+"\n")
    f.close()
    print self.weights
  
  def registerInitialState(self, gameState):
    #super(type(MyAgent)).registerInitialState(gameState)
    self.red = gameState.isOnRedTeam(self.index)
    import distanceCalculator
    self.distancer = distanceCalculator.Distancer(gameState.data.layout)

    # comment this out to forgo maze distance computation and use manhattan distances
    self.distancer.getMazeDistances()
    self.readWeights()
  

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """

    actions = gameState.getLegalActions(self.index)
    best = self.computeActionFromQValues(gameState)
    if not actions:
      toReturn = None
    if util.flipCoin(self.epsilon and self.training):
      toReturn = random.choice(actions)
    else:
      toReturn = best
    if toReturn != None and self.training:
      self.updateWeights(gameState, toReturn)
    #print self.weights
    #print self.index
    #print toReturn, best
    return toReturn

  def computeActionFromQValues(self, state):
    bestScore = self.computeValueFromQValues(state)
    if not state.getLegalActions(self.index):
      return 0
    actions = state.getLegalActions(self.index)
    for a in actions:
      if self.getQValue(state, a) == bestScore:
        return a
  def computeValueFromQValues(self, state):
      actions = state.getLegalActions(self.index)
      if not actions:
        return 0.0
      else:
        options = []
        for a in actions:
          options.append(self.getQValue(state,a))
        return max (options)

  def getQValue(self, state, actions):
    features = self.getFeatures(state, actions)
    return self.weights * features


  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    #this should decide how much we like a state and update the weights to reflect that
    #return 1
    return len(self.foodIWantToEat)

  def getFeatures(self, gameState, action):
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
    indecesOfMyTeam = []
    indecesOfOtherTeam = []
    for i in range(3):
      if IAmBlue and gameState.isOnRedTeam(i):
        indecesOfOtherTeam.append(i)
      else:
        indecesOfMyTeam.append(i)

    self.foodIwantToEat = []
    self.foodIwantToDefend = []
    if IAmBlue:
      self.foodIWantToEat = gameState.getRedFood().asList()
      self.foodIWantToDefend = gameState.getBlueFood().asList()
    else:
      self.foodIWantToEat = gameState.geBlueFood().asList()
      self.foodIWantToDefend = gameState.getRedFood().asList()

    


    distToClosestFood = min([self.distancer.getMazeDistance(gameState.getAgentPosition(self.index), f) for f in self.foodIwantToEat]+[1000])

    #print self.foodIWantToEat
    #features['FoodToEat'] = distToClosestFood
    a = len(self.foodIWantToEat)
    features['FoodLeft'] = a
    

    return features
  
  def updateWeights(self, gameState, action):

    newState = gameState.generateSuccessor(self.index, action)
    r= self.evaluate(newState, action)
    Q_of_SA = self.getQValue(gameState, action)
    weights = self.getWeights().copy()
    max = self.computeValueFromQValues(newState)

    difference = (r+self.discount*max) - Q_of_SA


    features = self.getFeatures(gameState, action)
    #print r, "reward"
    OldWeights= self.weights.copy()
    for f in features:
      #print f, weights[f], features[f]
      newVal = weights[f] + (self.alpha * difference *features[f])
      #print newVal, weights[f], f
      self.weights[f] = newVal

    self.weights.normalize()



  def getWeights(self):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return self.weights

