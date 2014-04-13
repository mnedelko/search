#e layout.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from util import manhattanDistance
from game import Grid
import os
import random

VISIBILITY_MATRIX_CACHE = {}

class Layout:
    """
    A Layout manages the static information about the game board.
    """
    ##[REF_LAYOUT111]:
    def __init__(self, layoutText):    ## The layoutText variable is furnished with the value of the tryToLayout function in form of a list [line1,line2,line2] of the layout file.
        self.width = len(layoutText[0])## measures the width of the first element in the layoutText list, which was passed in by the 'tryToLoad' function by initiating the Layout object in the function call below. Open one of the layout files in the 'layouts' folder to understand how the layout works.
        self.height= len(layoutText)   ## measures the hight of the layout by counting the length of the array [line1,line2,line3,line4]
        self.walls = Grid(self.width, self.height, False) ##self.walls contains an object that contains the Grid's width, height and a 2-dimenstional array called self.data that looks something like this:[[False, False, False,False],[False, False, False,False],...]
        self.food = Grid(self.width, self.height, False)  ## same as the line before
        self.capsules = []
        self.agentPositions = []
        self.numGhosts = 0
        self.processLayoutText(layoutText) ## This function takes the symbols contained in the layout files and turns them into coordinates which are then appended or assigned to the several variables that have been initialised in the code above. This happens according to the (x,y) convention used in the 2-dimensonal array that was defined in the Grid class.
        self.layoutText = layoutText   ## layoutText contains a list of lines row by row containing the layout information looking something like this [%.%OG%,.%OG%.%,%%%%%%,%....%]
        # self.initializeVisibilityMatrix()

    def getNumGhosts(self):
        return self.numGhosts  ## This number was recently increased with the implementation of the processLayoutText function below which forsees an increase of Ghost numbers whenever the layout file contains an G or an integer [1,2,3,4]

    def initializeVisibilityMatrix(self):
        global VISIBILITY_MATRIX_CACHE
        if reduce(str.__add__, self.layoutText) not in VISIBILITY_MATRIX_CACHE:
            from game import Directions
            vecs = [(-0.5,0), (0.5,0),(0,-0.5),(0,0.5)]
            dirs = [Directions.NORTH, Directions.SOUTH, Directions.WEST, Directions.EAST]
            vis = Grid(self.width, self.height, {Directions.NORTH:set(), Directions.SOUTH:set(), Directions.EAST:set(), Directions.WEST:set(), Directions.STOP:set()})
            for x in range(self.width):
                for y in range(self.height):
                    if self.walls[x][y] == False:
                        for vec, direction in zip(vecs, dirs):
                            dx, dy = vec
                            nextx, nexty = x + dx, y + dy
                            while (nextx + nexty) != int(nextx) + int(nexty) or not self.walls[int(nextx)][int(nexty)] :
                                vis[x][y][direction].add((nextx, nexty))
                                nextx, nexty = x + dx, y + dy
            self.visibility = vis
            VISIBILITY_MATRIX_CACHE[reduce(str.__add__, self.layoutText)] = vis
        else:
            self.visibility = VISIBILITY_MATRIX_CACHE[reduce(str.__add__, self.layoutText)]

    def isWall(self, pos):
        x, col = pos
        return self.walls[x][col]

    def getRandomLegalPosition(self):
        x = random.choice(range(self.width))
        y = random.choice(range(self.height))
        while self.isWall( (x, y) ):
            x = random.choice(range(self.width))
            y = random.choice(range(self.height))
        return (x,y)

    def getRandomCorner(self):
        poses = [(1,1), (1, self.height - 2), (self.width - 2, 1), (self.width - 2, self.height - 2)]
        return random.choice(poses)

    def getFurthestCorner(self, pacPos):
        poses = [(1,1), (1, self.height - 2), (self.width - 2, 1), (self.width - 2, self.height - 2)]
        dist, pos = max([(manhattanDistance(p, pacPos), p) for p in poses])
        return pos

    def isVisibleFrom(self, ghostPos, pacPos, pacDirection):
        row, col = [int(x) for x in pacPos]
        return ghostPos in self.visibility[row][col][pacDirection]

    def __str__(self):
        return "\n".join(self.layoutText)

    def deepCopy(self):
        return Layout(self.layoutText[:])

    def processLayoutText(self, layoutText):## This function is being called from the __init__ function of the Layout class. 
        """
        Coordinates are flipped from the input format to the (x,y) convention here

        The shape of the maze.  Each character
        represents a different type of object.## 
         % - Wall
         . - Food
         o - Capsule
         G - Ghost
         P - Pacman
        Other characters are ignored.
        """
        maxY = self.height - 1 # So that maxY was reduced by -1. This is critical as the loop below reduces maxY by y. The reduction is necessary as self.height was determined by len(layoutText) which counts all the elements but the for loop for the 'y' variable' uses range(self.height) which counts from '0'. maxY means that we are countin through the 2-dimensional array columns from the back to the front.
        for y in range(self.height): ## Why are we counting through the text elements in reverse? Because the __str__function of the Grid class returned the out variable which contains the GRID in reverse.
            for x in range(self.width): ### PLEASE NOTE! The need for reversing this is that we WANT TO LOOK AT THIS IN A COORDINATE FORMAT WITH (0,0) representing the bottom left corner.
                layoutChar = layoutText[maxY - y][x] #Passes the layout character ('%' '.' or 'o' --> see above or layout file) to the layoutChar variable. This is done in a 'flipped mannor from the input format to the (x,y) convention.
                ## Based on the 2D array the (visualized in file Grid_text) the layoutChar variable assumes the following values:
                self.processLayoutChar(x, y, layoutChar) # layoutChar is based on the variable layout Text: [%.%OG%,.%OG%.%,%%%%%%,%....%] with each position to be submited one-by-one based on the nested for loops. This maps the 2-dimentional Grid created in the __init__function and changes the boolean values to suit the layout of the board. See example in 'processLayoutChar' function below.
        self.agentPositions.sort()
        #print(self.agentPositions)
        self.agentPositions = [ ( i == 0, pos) for i, pos in self.agentPositions] #This basically creates a list of tuples containing the coordinates of the agents.
        #print(self.agentPositions)
        #print(self.capsules)
        #print(self.numGhosts)
        

    def processLayoutChar(self, x, y, layoutChar):
        if layoutChar == '%':        ## If the layoutChar happens to be '%' the 2-dimensional array of the self.walls instance will be changed from 'False' which happened to be the default as defined in game.py to True
            self.walls[x][y] = True  ## The wall object was created before in the __init__ function and returned by the __str__ function and contains a Grid comprising of a 2-dimensional array that looks something like this :[[False, False, False,False],[False, False, False,False],...]. But since this line evaluates the position of all wall-characters, certain elements within this nested list are now replaced bu 'True'.
        elif layoutChar == '.':
            self.food[x][y] = True
        elif layoutChar == 'o':
            self.capsules.append((x, y)) #This appends a tuple which denominates the coordinates of each capsule to the capsules instance.
        elif layoutChar == 'P':
            self.agentPositions.append( (0, (x, y) ) ) #This appends a two dimensional tuple that denominates the agent's position (and likely direction/ movement?!) -->WHAT IS THE AGENT FOR? Is it for the Ghosts or the AI AGENT? Its for the AI/ Player.
        elif layoutChar in ['G']:
            self.agentPositions.append( (1, (x, y) ) ) ## same as above, but this time it seems to be for the Ghost.
            self.numGhosts += 1
        elif layoutChar in  ['1', '2', '3', '4']:
            self.agentPositions.append( (int(layoutChar), (x,y))) ##STRANGE. No layout File features this! BUT this appears to be an option the developers allowed themselves. If the layoutChar is a particular number, it will be factored into the layout of this object? --> Yes. 1  to 4 could denominate certain directions.
            self.numGhosts += 1                                   ## If the layout file contains one of these numbers, the number of Ghosts is increased by 1.

def getLayout(name, back = 2):# This function takes a name as its argument and returns the corresponding layout from within the LAYOUT-Folder.
    if name.endswith('.lay'): # str.endswith(suffix[,start[,end]]) is part of the python Built-in Types. It returns True Return True if the string ends with the specified suffix
        layout = tryToLoad('layouts/' + name) # tryToLoad checks whether the file exists in the 'layouts' folder, opens the designated file, strips each line and returns it.
        if layout == None: layout = tryToLoad(name)
    else:
        layout = tryToLoad('layouts/' + name + '.lay')
        if layout == None: layout = tryToLoad(name + '.lay') ## This line attempts to load the layout if it cannot be found immediately in 'layout/<<layout_name>>.lay'.
    if layout == None and back >= 0:# This is a caviet in case the layout could not be found in the 'layouts' folder and hence hasn't been loaded int othe layout variable. If this variable prooves to be None, we will attempt to find the layout information recursively by backtracking the 3 folders that are preceeding the current folder 'layouts'.  
        curdir = os.path.abspath('.') 
        os.chdir('..') #chanes directory to the previous directory.
        layout = getLayout(name, back -1) # recursive call to see whether the file can be found by backtracking up to three stepps in the file-tree
        os.chdir(curdir) #changes the current directory back to the 'layouts' folder.
    return layout # THIS VARIABLE CONTAINS the LAYOUT OBJECT that was created by the LAYOUT CLASS --> See __init__method above for more detail.

def tryToLoad(fullname):
    if(not os.path.exists(fullname)): return None
    f = open(fullname)
    try: return Layout([line.strip() for line in f]) ##List comprehension that returns the 'LAYOUT' object of the layout class, by feeding it a list [line1, line2, line2...] of srtings that were stripped by its leading and trailig characters.The __init function above then makes a blue-print of the layout. SEE ABOVE
    finally: f.close()
