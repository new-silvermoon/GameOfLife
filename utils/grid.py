from . import cell
import numpy as np
Cell = cell.Cell

Patterns_dict ={
    'acorn': "/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/acorn.life",
    'beacon': "/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/beacon.life",
    'beehive': "/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/beehive.life",
    'blinker': "/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/blinker.life",
    'block': "/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/block.life",
    'boat': "/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/boat.life",
    'diehard': "/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/diehard.life",
    'glider': "/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/glider.life",
    'gosper-glider-gun': "/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/gosper-glider-gun.life",
    'infinite1': "/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/infinite1.life",
    'infinite2': "/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/infinite2.life",
    'infinite3': "/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/infinite3.life",
    'lightweight-spaceship': "/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/lightweight-spaceship.life",
    'loaf': "/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/loaf.life",
    'pentadecathlon': "/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/pentadecathlon.life",
    'pulsar': "/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/pulsar.life",
    'r-pentomino': "/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/r-pentomino.life",
    'toad': "/Users/stephanie/PycharmProjects/GameOfLife/utils/patterns/toad.life"
}

class Grid:
    """
    The cell automaton consists of a two dimensional grid populated with Cells
    """

    def __init__(self,width=80,height=23,cell_class = None):
        """

        :param width: Int. Width of the grid
        :param height: Int. Height of the grid
        :param cell_class: subclass of Cell
        """

        self.generation = 0
        self.width = int(width)
        self.height = int(height)

        if cell_class is None:
            cell_class = Cell

        assert issubclass(cell_class, Cell), 'expecting subclass of Cell, got {class_type}'.format(class_type=cell_class)

        self.cell_class = cell_class
        self.reset()

    @property
    def cells(self):

        try:
            return self._cells
        except AttributeError as e:
            pass

        self._cells = []
        return self._cells

    def __str__(self):
        s= []
        for y in range(self.height):
            r = ''
            for x in range(self.width):
                r+=str(self[x,y])
            s.append(r)

        return '\n'.join(s)

    def __repr__(self):
        s = ['{self.__class__.__name__}',
             '(cell_class={self.cell_class.__name__},',
             'width={self.width},',
             'height={self.height})']

        return ''.join(s).format(self=self)

    def addPattern(self,pattern,x=0,y=0,rule=None,eol='\n',resize=False):
        """

        Uses the pattern string to represent alive/dead cells in the grid
        Places the pattern at x,y coordinates in the grid.

        First character in the pattern string is placed at (0.0) coordinates

        Rule paramters helps in representing each character in the pattern
        in terms of alive or dead


        :param pattern: String
        :param x: Integer
        :param y: Integer
        :param rule: Function which returns boolean
        :param eol: End of line character in file
        :param resize: Boolean, Resizes the grid to pattern size
        :return: set of visited cells
        """

        try:
            pattern_path = Patterns_dict[pattern]
        except KeyError as e:
            print("No keys found in Pattern")
            return

        pattern = None
        with open(pattern_path) as f:
            pattern = f.read()

        if pattern is None:
            print("No pattern found ")
            return

        if rule is None:
            rule = lambda  c: not c.isspace()

        if resize:
            self.height = len(pattern.split(eol))
            self.width = max([len(l) for l in pattern.split(eol)])
            self.reset()

        visited = set()

        for j,line in enumerate(pattern.split(eol)):
            for i,chars in enumerate(line):
                self[x+i,y+j].alive = int(rule(chars))
                visited.add(self[x+i,y+j])
        return visited

    def writeToFile(self,fileObj):

        try:
            num_of_bytes = fileObj.write(str(self))
            return num_of_bytes
        except AttributeError as e:
            pass

        with open(fileObj, 'w') as f:
            num_of_bytes = f.write(str(self))
            return num_of_bytes

    def readFromFile(self,fileObj,rule=None,eol='\n'):
        pattern = None
        try:
            pattern = fileObj.read()
        except AttributeError as e:
            with open(fileObj) as f:
                pattern = f.read()

        self.addPattern(pattern,resize=True)

    def warpCells(self,key):
        """
        warps cell at x,y coordinates
        :param key: list of x,y int values
        :return:
        """

        x,y = map(int,key)
        x %= self.width
        y %= self.height
        return x, y

    def __getitem__(self, item):
        """

        :param item: Int
        :return: List of cells
        """

        try:
            x,y = self.warpCells(item)
            return self.cells[(y*self.width) + x]
        except TypeError:
            pass

        return self.cells[item]

    def reset(self):
        """
        Rests the Grid to original state
        - set Generation = 0
        - all cells are deleted and new cells are allocated
        :return: None
        """

        self.generation = 0
        self.cells.clear()

        for y in range(self.height):
            for x in range(self.height):
                self.cells.append(self.cell_class(x,y))


        for cell in self.cells:
            cell.neighbors.extend([self[i] for i in cell.neighborLocations])

    def advanceGen(self):
        """
        Increases generation count of the organisms by 1

        - All cells are updated with the current count of alive neighbors

        - All cell determine their next state

        :return: None
        """

        self.generation += 1

        for cell in self:
            cell.update()

        for cell in self:
            cell.decideLife()

class BaseGrid(Grid):

    def __init__(self,width=80,height=23):
        self.generation = 0
        self.width = int(width)
        self.height = int(height)
        self.markers =['','.']

    def __str__(self):
        '''
        '''
        s = []
        for y in range(self.height):
            r = ''
            for x in range(self.width):
                r += self.markers[self.cells[y, x] > 0]
            s.append(r)
        return '\n'.join(s)

    def __repr__(self):
        '''
        '''
        s = ['{self.__class__.__name__}',
             '(width={self.width},',
             'height={self.height})']

        return ''.join(s).format(self=self)

    @property
    def cells(self):
        try:
            return self._cells
        except AttributeError as e:
            pass

        self._cells = np.zeros((self.height,self.width),dtype=np.int)
        return self._cells

    @property
    def state(self):
        try:
            return self._state
        except AttributeError as e:
            pass
        self._state = np.zeros((self.height,self.width), dtype=np.int)
        return self._state

    @property
    def alive(self):
        """

        :return: list of (x,y) coordinates of cells which are alive
        """
        cells = self.cells.nonzero()
        return [(x,y) for x,y in zip(cells[1],cells[0])]

    def warpCells(self,key):
        x,y = key
        height, width = self.cells.shape
        return (x%(width -1),y%(height -1))

    def __getitem__(self, key):
        x, y = self.warpCells(key)
        return self.cells[y, x]

    def __setitem__(self, key, value):
        x, y = self.warpCells(key)
        self.cells[y, x] = value

    def __iter__(self):
        self._x = 0
        self._y = 0
        return self

    def next(self):
        coord_cell = self[self._x,self._y]
        x,y = self._x,self._y
        self._x +=1
        if self._x not in range(self.width):
            self._x = 0
            self._y+=1
        if self._y not in range(self.height):
            raise StopIteration

        return x,y,coord_cell

    def addPattern(self,pattern,x=0,y=0,rule=None,eol='\n',resize=False):
        """

        Uses the pattern string to represent alive/dead cells in the grid
        Places the pattern at x,y coordinates in the grid.

        First character in the pattern string is placed at (0.0) coordinates

        Rule paramters helps in representing each character in the pattern
        in terms of alive or dead


        :param pattern: String
        :param x: Integer
        :param y: Integer
        :param rule: Function which returns boolean
        :param eol: End of line character in file
        :param resize: Boolean, Resizes the grid to pattern size
        :return: set of visited cells
        """

        try:
            pattern_path = Patterns_dict[pattern]
        except KeyError as e:
            print("No keys found in Pattern")
            return

        pattern = None
        with open(pattern_path) as f:
            pattern = f.read()

        if pattern is None:
            print("No pattern found ")
            return

        if rule is None:
            rule = lambda  c: not c.isspace()

        if resize:
            self.height = len(pattern.split(eol))
            self.width = max([len(l) for l in pattern.split(eol)])
            self.reset()

        visited = set()

        for j,line in enumerate(pattern.split(eol)):
            for i,chars in enumerate(line):
                self[x+i,y+j] = int(rule(chars))
                visited.add(self[x+i,y+j])
        return visited

    def reset(self):
        """
        Rests the Grid to original state
        - set Generation = 0
        - all cells are filled with zero
        :return: None
        """

        self.generation = 0
        self.cells.fill(0)

    def neighborLocation(self,x,y):
        """
        Yields the coordinates of neighboring cells
        """
        yield (x - 1, y - 1)
        yield (x, y - 1)
        yield (x + 1, y - 1)
        yield (x - 1, y)
        yield (x, y)
        yield (x + 1, y)
        yield (x - 1, y + 1)
        yield (x, y + 1)
        yield (x + 1, y + 1)

    def calculateState(self,x,y,born_rule=None,alive_rule=None):
        if born_rule is None:
            born_rule = [3]

        if alive_rule is None:
            alive_rule =[2,3]

        # Creating a 3x3 grid for neighboring cells of cell at x,y

        neighbors = np.array([self[cell] for cell in self.neighborLocation(x,y)]) > 0
        #neighbors = np.array([self[cell] for cell in self.neighborLocation(x, y)])
        neighbors.shape = (3,3)
        neighbors[1,1] = 0

        sum_neighbors = neighbors.sum()

        #Initial assumption is dead
        state = 0

        if(self[x,y] == 0) and (sum_neighbors in born_rule):
            state = 1

        if(self[x,y] > 0) and (sum_neighbors in alive_rule):
            state = self[x,y] + 1

        self.state[y,x] = state

    def updateState(self):
        self.state.fill(0)
        for x,y in self.candidates:
            self.calculateState(x,y)

    def updateCells(self):
        alive = self.state.nonzero()
        self.cells.fill(0)
        self.cells[alive] = self.state[alive]

    @property
    def candidates(self):
        """

        :return: x,y coordinates sof the cell is the grid
        """

        for y in range(self.height):
            for x in range(self.width):
                yield (x,y)

    def advanceGen(self):
        self.updateState()
        self.updateCells()
        self.generation +=1


    def startAdvancingGen(self,steps=-1):
        try:
            while self.generation != steps:
                print(self)
                self.advanceGen()
        except Exception as e:
            pass

class OptmizedBaseGrid(BaseGrid):
    @property
    def candidates(self):
        cand_set = set()

        for x,y in self.alive:
            for key in self.neighborLocation(x,y):
                cand_set.add(self.warpCells(key))

        return cand_set











