# game.py
# -------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from util import *
import time, os
import traceback

#######################
# Parts worth reading #
#######################

class Agent:
    """
    An agent must define a getAction method, but may also define the
    following methods which will be called if they exist:

    def registerInitialState(self, state): # inspects the starting state
    """
    def __init__(self, index=0):
        self.index = index

    def getAction(self, state):
        """
        The Agent will receive a GameState (from either {pacman, capture, sonar}.py) and
        must return an action from Directions.{North, South, East, West, Stop}
        """
        raiseNotDefined()

class Directions:
    NORTH = 'North'
    SOUTH = 'South'
    EAST = 'East'
    WEST = 'West'
    STOP = 'Stop'

    LEFT =       {NORTH: WEST,
                   SOUTH: EAST,
                   EAST:  NORTH,
                   WEST:  SOUTH,
                   STOP:  STOP}

    RIGHT =      dict([(y,x) for x, y in LEFT.items()])

    REVERSE = {NORTH: SOUTH,
               SOUTH: NORTH,
               EAST: WEST,
               WEST: EAST,
               STOP: STOP}

class Configuration:  #[REF 113]#Configuratin is first called from within the GameStateData class's initializa method: self.agentStates.append( AgentState( Configuration( pos, Directions.STOP), isPacman) )
    """
    A Configuration holds the (x,y) coordinate of a character, along with its
    traveling direction.

    The convention for positions, like a graph, is that (0,0) is the lower left corner, x increases
    horizontally and y increases vertically.  Therefore, north is the direction of increasing y, or (0,1).
    """

    def __init__(self, pos, direction):
        self.pos = pos                   ##Position is passed on by the self.agentStates.append function in the GameStateData class. Position here comprises of a tuple indicating coordinates on the game-board.
        self.direction = direction

    def getPosition(self):
        return (self.pos)

    def getDirection(self):
        return self.direction

    def isInteger(self):
        x,y = self.pos
        return x == int(x) and y == int(y)

    def __eq__(self, other):
        if other == None: return False
        return (self.pos == other.pos and self.direction == other.direction)

    def __hash__(self):
        x = hash(self.pos)
        y = hash(self.direction)
        return hash(x + 13 * y)

    def __str__(self):
        return "(x,y)="+str(self.pos)+", "+str(self.direction)

    def generateSuccessor(self, vector):
        """
        Generates a new configuration reached by translating the current
        configuration by the action vector.  This is a low-level call and does
        not attempt to respect the legality of the movement.

        Actions are movement vectors.
        """
        x, y= self.pos
        dx, dy = vector
        direction = Actions.vectorToDirection(vector)
        if direction == Directions.STOP:
            direction = self.direction # There is no stop direction
        return Configuration((x + dx, y+dy), direction)

class AgentState:                        #[REF 114]# AgentState takes the initialized Configuration object from the Configuration class as a startConfiguration attribute. 
    """
    AgentStates hold the state of an agent (configuration, speed, scared, etc).
    """

    def __init__( self, startConfiguration, isPacman ): ## isPacman is TRUE if it is the Pacman(aka Player or AI) or FALSE if it is a ghost.
        self.start = startConfiguration                 ## interesting: self.start and self.configuration is only the same when a new game commences
        self.configuration = startConfiguration         ## Once a new game begins self.configuration must be different  
        self.isPacman = isPacman
        self.scaredTimer = 0
        #print(str(self.configuration))

    def __str__( self ):
        if self.isPacman:
            return "Pacman: " + str( self.configuration )
        else:
            return "Ghost: " + str( self.configuration )

    def __eq__( self, other ):
        if other == None:
            return False
        return self.configuration == other.configuration and self.scaredTimer == other.scaredTimer

    def __hash__(self):
        return hash(hash(self.configuration) + 13 * hash(self.scaredTimer))

    def copy( self ):
        state = AgentState( self.start, self.isPacman )
        state.configuration = self.configuration
        state.scaredTimer = self.scaredTimer
        return state

    def getPosition(self):
        if self.configuration == None: return None
        return self.configuration.getPosition()

    def getDirection(self):
        return self.configuration.getDirection()

class Grid: ##This class is initiated through a function call situated within the __init__ function of the Layout class. The class objects Layout.width, layout.height are passed to the Grid__init__function as width and height variables. 
    """
    A 2-dimensional array of objects backed by a list of lists.  Data is accessed
    via grid[x][y] where (x,y) are positions on a Pacman map with x horizontal,
    y vertical and the origin (0,0) in the bottom left corner.

    The __str__ method constructs an output that is oriented like a pacman board.
    """
    def __init__(self, width, height, initialValue=False, bitRepresentation=None):
        if initialValue not in [False, True]: raise Exception('Grids can only contain booleans')
        self.CELLS_PER_INT = 30 ## 
        
        self.width = width ## the Grid object instance uses the Layout.width and layout height variables as the height and width objects of the Grid class.
        self.height = height
        ##[REF112]: self.data is being called by many functions. Amongst others it is directly called by pacman.py's GameState.initialize function.
        self.data = [[initialValue for y in range(height)] for x in range(width)] ##So this creates a 2-dimensional array that looks something like this: [[False, False, False, False][False, False, False, False]] Why do we do it that way around? Because when invoking the __str__ initializer we are going to work with a nexted list comprehension again to walk through the 2D array. SEE seperate file: 'GRID_TEXT' for example.
        ## NOTE: The two dimensional array lies on its side. Height extends to the left and width extends to the top. Thi is later corrected below [REF-113].
        if bitRepresentation:
            self._unpackBits(bitRepresentation)

    def __getitem__(self, i): ##So __getitem__ and __setitem__ are usually standard methods Python calls for you. These are working behind the scenes and are defined in the background. But just as easily as these are defined for your behind the scenes you can redefine them to give them a more customized functionality. This is what is happening here.
        return self.data[i]   ## Here we will make sure that if we call for the value of the self.data array we will make sure it returns the value that can be found at the requested key.

    def __setitem__(self, key, item):
        self.data[key] = item ## Here we define the bahviour of the self.data object to ensure that if we wanted to add something, we can. Is THIS LIKE A DICTIONARY?

    def __str__(self):        ## The __str__ function returns the Grid objects self.width, self.height, self.data in a string format.
        out = [[str(self.data[x][y])[0] for x in range(self.width)] for y in range(self.height)] ## Makes the 2-dimensional array into: ['F', 'F', 'F', 'F', 'F', 'F'], ['F', 'F', 'F', 'F', 'F', 'F'], ['F', 'F', 'F', 'F', 'F', 'F'], ['F', 'F', 'F', 'F', 'F', 'F'], ['F', 'F', 'F', 'F', 'F', 'F']]
        ## [REF-113] NOTE: This actually transforms the 2D array which used to lie on its right side into the propper 2D array standing up. 
        out.reverse() #reverses the oder of with the last row of the two dimensional array becoming the first row.
        return '\n'.join([''.join(x) for x in out]) #every line is appended with a space '' followed by a line-break with '\n'
        # This turns the Grid into a chessboard of F's by using the \n demarcator.
        ## F F F F F
        ## F F F F F
        ## F F F F F
        ## F F F F F

    def __eq__(self, other): # The __eq__ method compares other instances of the class with itself
        if other == None: return False
        return self.data == other.data # This highlights that it may be TRUE or FALSE?

    def __hash__(self):
        '''The __hash__() function just returns an integer. It is called from the built-in function hash().
         The key property of the hash function is that if two boards are equivalent, calling __hash__ on them will give the same number. If the boards are different, it is good (but not required) for their hashes to be different.
         Hash functions are most commonly used by hashtables, but the hash function itself does not create or use a hashtable. The call to hash(h) simply converts h from a possibly huge number to a 32 bit integer.'''
        # return hash(str(self))
        base = 1
        h = 0
        for l in self.data:
            for i in l:
                if i:
                    h += base
                base *= 2
        return hash(h)

    def copy(self):
        g = Grid(self.width, self.height)
        g.data = [x[:] for x in self.data]
        return g

    def deepCopy(self):
        return self.copy()

    def shallowCopy(self):
        g = Grid(self.width, self.height)
        g.data = self.data
        return g

    def count(self, item =True ):
        return sum([x.count(item) for x in self.data])

    def asList(self, key = True):
        list = []
        for x in range(self.width):
            for y in range(self.height):
                if self[x][y] == key: list.append( (x,y) )
        return list

    def packBits(self):
        """
        Returns an efficient int list representation

        (width, height, bitPackedInts...)
        """
        bits = [self.width, self.height]
        currentInt = 0
        for i in range(self.height * self.width):
            bit = self.CELLS_PER_INT - (i % self.CELLS_PER_INT) - 1
            x, y = self._cellIndexToPosition(i)
            if self[x][y]:
                currentInt += 2 ** bit
            if (i + 1) % self.CELLS_PER_INT == 0:
                bits.append(currentInt)
                currentInt = 0
        bits.append(currentInt)
        return tuple(bits)

    def _cellIndexToPosition(self, index):
        x = index / self.height
        y = index % self.height
        return x, y

    def _unpackBits(self, bits):
        """
        Fills in data from a bit-level representation
        """
        cell = 0
        for packed in bits:
            for bit in self._unpackInt(packed, self.CELLS_PER_INT):
                if cell == self.width * self.height: break
                x, y = self._cellIndexToPosition(cell)
                self[x][y] = bit
                cell += 1

    def _unpackInt(self, packed, size):
        bools = []
        if packed < 0: raise ValueError, "must be a positive integer"
        for i in range(size):
            n = 2 ** (self.CELLS_PER_INT - i - 1)
            if packed >= n:
                bools.append(True)
                packed -= n
            else:
                bools.append(False)
        return bools

def reconstituteGrid(bitRep):
    if type(bitRep) is not type((1,2)):
        return bitRep
    width, height = bitRep[:2]
    return Grid(width, height, bitRepresentation= bitRep[2:])

####################################
# Parts you shouldn't have to read #
####################################

class Actions:
    """
    A collection of static methods for manipulating move actions.
    """
    # Directions
    _directions = {Directions.NORTH: (0, 1),
                   Directions.SOUTH: (0, -1),
                   Directions.EAST:  (1, 0),
                   Directions.WEST:  (-1, 0),
                   Directions.STOP:  (0, 0)}

    _directionsAsList = _directions.items()

    TOLERANCE = .001

    def reverseDirection(action):
        if action == Directions.NORTH:
            return Directions.SOUTH
        if action == Directions.SOUTH:
            return Directions.NORTH
        if action == Directions.EAST:
            return Directions.WEST
        if action == Directions.WEST:
            return Directions.EAST
        return action
    reverseDirection = staticmethod(reverseDirection)

    def vectorToDirection(vector):
        dx, dy = vector
        if dy > 0:
            return Directions.NORTH
        if dy < 0:
            return Directions.SOUTH
        if dx < 0:
            return Directions.WEST
        if dx > 0:
            return Directions.EAST
        return Directions.STOP
    vectorToDirection = staticmethod(vectorToDirection)

    def directionToVector(direction, speed = 1.0):
        dx, dy =  Actions._directions[direction]
        return (dx * speed, dy * speed)
    directionToVector = staticmethod(directionToVector)

    def getPossibleActions(config, walls):##This function is being called in pacman.py and is returned and as part of the PacmanRules class's getLegalActions functions
        possible = []
        x, y = config.pos ## REF-211 in Pacman.py this function is called and state.getPacmanState().configuration is passed as config as an argument.
        x_int, y_int = int(x + 0.5), int(y + 0.5)

        # In between grid points, all agents must continue straight
        if (abs(x - x_int) + abs(y - y_int)  > Actions.TOLERANCE):
            return [config.getDirection()]

        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_y = y_int + dy
            next_x = x_int + dx
            if not walls[next_x][next_y]: possible.append(dir)

        return possible

    getPossibleActions = staticmethod(getPossibleActions)

    def getLegalNeighbors(position, walls):
        x,y = position
        x_int, y_int = int(x + 0.5), int(y + 0.5)
        neighbors = []
        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_x = x_int + dx
            if next_x < 0 or next_x == walls.width: continue
            next_y = y_int + dy
            if next_y < 0 or next_y == walls.height: continue
            if not walls[next_x][next_y]: neighbors.append((next_x, next_y))
        return neighbors
    getLegalNeighbors = staticmethod(getLegalNeighbors)

    def getSuccessor(position, action):
        dx, dy = Actions.directionToVector(action)
        x, y = position
        return (x + dx, y + dy)
    getSuccessor = staticmethod(getSuccessor)

class GameStateData:
    """
    The GameStateData is initialised into the self.data variable, in pacman1.py's GameState __init__.
    It only takes the previousState as an attribute, but only if this previous GameState does in fact excists.
    This is not the case when a new game commences.
    """
    def __init__( self, prevState = None ):
        """
        Generates a new data packet by copying information from its predecessor.
        """
        if prevState != None:
            self.food = prevState.food.shallowCopy()
            self.capsules = prevState.capsules[:]
            self.agentStates = self.copyAgentStates( prevState.agentStates )
            self.layout = prevState.layout
            self._eaten = prevState._eaten
            self.score = prevState.score
        self._foodEaten = None
        self._capsuleEaten = None
        self._agentMoved = None
        self._lose = False
        self._win = False
        self.scoreChange = 0

    def deepCopy( self ):                       ## What is .deepCopy()? If only copied state.food by doing state.food = self.food, both variables would still point to the same memory location.
        state = GameStateData( self )           ## The problem with that ins that, if we make changed to one, the change will automatically be reflected in the variable we copied to as it points to the same pice of memnory.  this changes. 
        state.food = self.food.deepCopy()       ## This is different with deepCopy() created a new object with different memory locations. 
        state.layout = self.layout.deepCopy()   ## This means that changing one variable will in no way affect the other variable, as neither the variable itself nor the object points to the same memory address.
        state._agentMoved = self._agentMoved    ## Its like a new variable with new content was created.
        state._foodEaten = self._foodEaten
        state._capsuleEaten = self._capsuleEaten
        return state

    def copyAgentStates( self, agentStates ):
        copiedStates = []
        for agentState in agentStates:
            copiedStates.append( agentState.copy() )
        return copiedStates

    def __eq__( self, other ):
        """
        Allows two states to be compared.
        """
        if other == None: return False
        # TODO Check for type of other
        if not self.agentStates == other.agentStates: return False
        if not self.food == other.food: return False
        if not self.capsules == other.capsules: return False
        if not self.score == other.score: return False
        return True

    def __hash__( self ):
        """
        Allows states to be keys of dictionaries.
        """
        for i, state in enumerate( self.agentStates ):
            try:
                int(hash(state))
            except TypeError, e:
                print e
                #hash(state)
        return int((hash(tuple(self.agentStates)) + 13*hash(self.food) + 113* hash(tuple(self.capsules)) + 7 * hash(self.score)) % 1048575 )

    def __str__( self ):
        width, height = self.layout.width, self.layout.height
        map = Grid(width, height)
        if type(self.food) == type((1,2)):
            self.food = reconstituteGrid(self.food)
        for x in range(width):
            for y in range(height):
                food, walls = self.food, self.layout.walls
                map[x][y] = self._foodWallStr(food[x][y], walls[x][y])

        for agentState in self.agentStates:
            if agentState == None: continue
            if agentState.configuration == None: continue
            x,y = [int( i ) for i in nearestPoint( agentState.configuration.pos )]
            agent_dir = agentState.configuration.direction
            if agentState.isPacman:
                map[x][y] = self._pacStr( agent_dir )
            else:
                map[x][y] = self._ghostStr( agent_dir )

        for x, y in self.capsules:
            map[x][y] = 'o'

        return str(map) + ("\nScore: %d\n" % self.score)

    def _foodWallStr( self, hasFood, hasWall ):
        if hasFood:
            return '.'
        elif hasWall:
            return '%'
        else:
            return ' '

    def _pacStr( self, dir ):
        if dir == Directions.NORTH:
            return 'v'
        if dir == Directions.SOUTH:
            return '^'
        if dir == Directions.WEST:
            return '>'
        return '<'

    def _ghostStr( self, dir ):
        return 'G'
        if dir == Directions.NORTH:
            return 'M'
        if dir == Directions.SOUTH:
            return 'W'
        if dir == Directions.WEST:
            return '3'
        return 'E'

    def initialize( self, layout, numGhostAgents ):##[REF112] This function is being called by the initialize function in the GameState class. While the GameStateData __init__ just initializes the data object containing all sorts of information about the Game state, this function populates this information.Layout is passed on by the initialize method to which it was passed by initState.initialize contained within the newGamemethod. 
        """
        Creates an initial game state from a layout array (see layout.py).

        layout contains
        """
        self.food = layout.food.copy()     ##makes a copy of the layout.food list which contains a list of lists specifying the location of food dots by via a grid of True and False. it should look something like this:[['F','F','True','F']['F','F','True','F']['F','F','True','F']['F','F','True','F']] 
        self.capsules = layout.capsules[:] 
        self.layout = layout
        self.score = 0
        self.scoreChange = 0

        self.agentStates = []
        numGhosts = 0
        for isPacman, pos in layout.agentPositions:## layout.agentPositions looks something like this [(True, (9, 1)), (False, (8 5)), (False, (11, 5))].All these are looped through. TRUE denominates the pacman and its coordinates which are contained in the tuple. 
            if not isPacman:                       ## This basically goes: if FALSE (so if this is not the pacman) and
                if numGhosts == numGhostAgents: continue # if the Max ghosts hasn't been reached yet
                else: numGhosts += 1
            #print(str(Configuration( pos, Directions.STOP)))   
            self.agentStates.append( AgentState( Configuration( pos, Directions.STOP), isPacman) ) #CONFIGURATION [REF 113]# #AGENTSTATE [REF 114] AgentStates hold the state of an agent (start, configuration, isPacman, scared, etc).
        #print(str(self.agentStates))
        self._eaten = [False for a in self.agentStates]  ##what is self._eaten?

try:
    import boinc
    _BOINC_ENABLED = True
except:
    _BOINC_ENABLED = False

class Game:
    """
    The Game manages the control flow, soliciting actions from agents.  This class is first initialized by the newGame method in the ClassicGameRules class [REF 115]
    """

    def __init__( self, agents, display, rules, startingIndex=0, muteAgents=False, catchExceptions=False ):
        self.agentCrashed = False
        self.agents = agents                                           ## agents contain the pacman and ghost agent objects combigned into a list of lists agents = [pacmanAgent] + ghostAgents[:layout.getNumGhosts()]
        self.display = display                                         #[REF116] --> pacman1.py# display is display contains the display object which specifies display elements such as:  self.have_window = 0, self.currentGhostImages = {}, self.pacmanImage = None, self.zoom = zoom, self.gridSize = DEFAULT_GRID_SIZE * zoom, self.capture = capture, self.frameTime= frameTime
        #print("This is the display object" + str(self.display))
        self.rules = rules                                             ## The rules are passed on as the self attribute of the ClassicGameRules class within the call of Game in newGame [REF 115].
        self.startingIndex = startingIndex                             ## starting index is given as default attribute by the __init__ method.
        self.gameOver = False
        self.muteAgents = muteAgents
        self.catchExceptions = catchExceptions
        self.moveHistory = []
        self.totalAgentTimes = [0 for agent in agents]                 ## This creates a list that replaces the list elements of the agents list, which contains the agent objects, with zeros. It looks something like this [0,0,0]
        ##print(self.totalAgentTimes)
        self.totalAgentTimeWarnings = [0 for agent in agents]          
        self.agentTimeout = False
        import cStringIO                                               ## Building long strings in the Python progamming language can sometimes result in very slow running code.The cStringIO module provides a class called StringIO that works like a file, but is stored as a string. Obviously it's easy to append to a file - you simply write at the end of it and the same is true for this module. There is a similar module called just StringIO, but that's implemented in python whereas cStringIO is in C. It should be pretty speedy. Using this object we can build our string one write at a time and then collect the result using the getvalue() call.
        self.agentOutput = [cStringIO.StringIO() for agent in agents]  ## This line uses the StringIO method from the cSringIO module to save the string in a pseudo-file to increase the speed.

    def getProgress(self):
        if self.gameOver:
            return 1.0
        else:
            return self.rules.getProgress(self)

    def _agentCrash( self, agentIndex, quiet=False):
        "Helper method for handling agent crashes"
        if not quiet: traceback.print_exc()
        self.gameOver = True
        self.agentCrashed = True
        self.rules.agentCrash(self, agentIndex)

    OLD_STDOUT = None
    OLD_STDERR = None

    def mute(self, agentIndex):
        if not self.muteAgents: return
        global OLD_STDOUT, OLD_STDERR
        import cStringIO
        OLD_STDOUT = sys.stdout
        OLD_STDERR = sys.stderr
        sys.stdout = self.agentOutput[agentIndex]
        sys.stderr = self.agentOutput[agentIndex]

    def unmute(self):
        if not self.muteAgents: return
        global OLD_STDOUT, OLD_STDERR
        # Revert stdout/stderr to originals
        sys.stdout = OLD_STDOUT
        sys.stderr = OLD_STDERR


    def run( self ):                                                   ## Called by the runGames method within the pacman1.py module
        """
        Main control loop for game play.                               ## [REF 115] # This initializes the display method within the PacmanGraphics calss of the graphicsDisplay.py module
        """
        #print(self.state.data)
        self.display.initialize(self.state.data)                       ## self.state.data was first defined in the GameSate __init__ function as self.data = GameStateData() GameStateData .It is then initialized via a call to the GameState.initialize method from within the newGame function: which creates an initial game state from a layout array.
        self.numMoves = 0                                              # [REF 117] # self.display.initialize. This is where we initialize the graphics.

        ###self.display.initialize(self.state.makeObservation(1).data)
        # inform learning agents of the game start
        for i in range(len(self.agents)):
            agent = self.agents[i]
            if not agent:
                self.mute(i)
                # this is a null agent, meaning it failed to load
                # the other team wins
                print "Agent %d failed to load" % i
                self.unmute()
                self._agentCrash(i, quiet=True)
                return
            if ("registerInitialState" in dir(agent)):
                self.mute(i)
                if self.catchExceptions:
                    try:
                        timed_func = TimeoutFunction(agent.registerInitialState, int(self.rules.getMaxStartupTime(i)))
                        try:
                            start_time = time.time()
                            timed_func(self.state.deepCopy())
                            time_taken = time.time() - start_time
                            self.totalAgentTimes[i] += time_taken
                        except TimeoutFunctionException:
                            print "Agent %d ran out of time on startup!" % i
                            self.unmute()
                            self.agentTimeout = True
                            self._agentCrash(i, quiet=True)
                            return
                    except Exception,data:
                        self._agentCrash(i, quiet=False)
                        self.unmute()
                        return
                else:
                    agent.registerInitialState(self.state.deepCopy())
                ## TODO: could this exceed the total time
                self.unmute()

        agentIndex = self.startingIndex
        numAgents = len( self.agents )

        while not self.gameOver:
            # Fetch the next agent
            agent = self.agents[agentIndex]
            move_time = 0
            skip_action = False
            # Generate an observation of the state
            if 'observationFunction' in dir( agent ):
                self.mute(agentIndex)
                if self.catchExceptions:
                    try:
                        timed_func = TimeoutFunction(agent.observationFunction, int(self.rules.getMoveTimeout(agentIndex)))
                        try:
                            start_time = time.time()
                            observation = timed_func(self.state.deepCopy())
                        except TimeoutFunctionException:
                            skip_action = True
                        move_time += time.time() - start_time
                        self.unmute()
                    except Exception,data:
                        self._agentCrash(agentIndex, quiet=False)
                        self.unmute()
                        return
                else:
                    observation = agent.observationFunction(self.state.deepCopy())
                self.unmute()
            else:
                observation = self.state.deepCopy()

            # Solicit an action
            action = None
            self.mute(agentIndex)
            if self.catchExceptions:
                try:
                    timed_func = TimeoutFunction(agent.getAction, int(self.rules.getMoveTimeout(agentIndex)) - int(move_time))
                    try:
                        start_time = time.time()
                        if skip_action:
                            raise TimeoutFunctionException()
                        action = timed_func( observation )
                    except TimeoutFunctionException:
                        print "Agent %d timed out on a single move!" % agentIndex
                        self.agentTimeout = True
                        self._agentCrash(agentIndex, quiet=True)
                        self.unmute()
                        return

                    move_time += time.time() - start_time

                    if move_time > self.rules.getMoveWarningTime(agentIndex):
                        self.totalAgentTimeWarnings[agentIndex] += 1
                        print "Agent %d took too long to make a move! This is warning %d" % (agentIndex, self.totalAgentTimeWarnings[agentIndex])
                        if self.totalAgentTimeWarnings[agentIndex] > self.rules.getMaxTimeWarnings(agentIndex):
                            print "Agent %d exceeded the maximum number of warnings: %d" % (agentIndex, self.totalAgentTimeWarnings[agentIndex])
                            self.agentTimeout = True
                            self._agentCrash(agentIndex, quiet=True)
                            self.unmute()

                    self.totalAgentTimes[agentIndex] += move_time
                    #print "Agent: %d, time: %f, total: %f" % (agentIndex, move_time, self.totalAgentTimes[agentIndex])
                    if self.totalAgentTimes[agentIndex] > self.rules.getMaxTotalTime(agentIndex):
                        print "Agent %d ran out of time! (time: %1.2f)" % (agentIndex, self.totalAgentTimes[agentIndex])
                        self.agentTimeout = True
                        self._agentCrash(agentIndex, quiet=True)
                        self.unmute()
                        return
                    self.unmute()
                except Exception,data:
                    self._agentCrash(agentIndex)
                    self.unmute()
                    return
            else:
                action = agent.getAction(observation)
            self.unmute()

            # Execute the action
            self.moveHistory.append( (agentIndex, action) )
            if self.catchExceptions:
                try:
                    self.state = self.state.generateSuccessor( agentIndex, action )
                except Exception,data:
                    self.mute(agentIndex)
                    self._agentCrash(agentIndex)
                    self.unmute()
                    return
            else:
                self.state = self.state.generateSuccessor( agentIndex, action )

            # Change the display
            self.display.update( self.state.data )
            ###idx = agentIndex - agentIndex % 2 + 1
            ###self.display.update( self.state.makeObservation(idx).data )

            # Allow for game specific conditions (winning, losing, etc.)
            self.rules.process(self.state, self)
            # Track progress
            if agentIndex == numAgents + 1: self.numMoves += 1
            # Next agent
            agentIndex = ( agentIndex + 1 ) % numAgents

            if _BOINC_ENABLED:
                boinc.set_fraction_done(self.getProgress())

        # inform a learning agent of the game result
        for agentIndex, agent in enumerate(self.agents):
            if "final" in dir( agent ) :
                try:
                    self.mute(agentIndex)
                    agent.final( self.state )
                    self.unmute()
                except Exception,data:
                    if not self.catchExceptions: raise
                    self._agentCrash(agentIndex)
                    self.unmute()
                    return
        self.display.finish()
