import hashlib

class Cell:

    """
    Defines one cell in the cell automaton
    """

    alive_rule = [3]
    death_rule = [0,1,4,5,6,7,8]

    def __init__(self,x,y,alive=False,markers=' .'):
        """

        :param x: x coordinate. Int
        :param y: y coordinate. Int
        :param alive: is the organism alive in the cell. Bool
        :param markers: Characters to be placed on alive cell. String
        """

        assert len(markers) > 1, "Marker length should be atleast 2 chars"

        self.location =  (x,y)
        self.markers = markers
        self.aliveNeighbors = 0
        self.alive = alive
        self.age = 0

    def isAlive(self):
        try:
            return self._alive
        except AttributeError as e:
            pass
        self._alive = False
        self.age = 0
        return self._alive

    def setAlive(self, value):
        self._alive = bool(value)
        if not self._alive:
            self.age = 0

    def __str__(self):
        """
        :return: Indicates cell's state as markers
        """

        return self.markers[int(self.alive)]

    def __repr__(self):
        s = ['{self.__class__.__name__}',
             '(x={self.location[0]!r},',
             'y={self.location[1]!r},',
             'alive={self.alive!r},',
             'markers={self.markers!r})']

        return ''.join(s).format(self=self)

    def __hash__(self):
        """

        :return: Integer hash for a cell which does not vary in it's life time
        """

        try:
            return self._hash
        except AttributeError as e:
            pass

        self._hash = int(hashlib.sha1(bytes(repr(self),'utf-8')).hexdigest(),16)

        return self._hash

    @property
    def neighbors(self):
        try:
            return self._neighbors
        except AttributeError as e:
            pass

        self._neighbors = []
        return self._neighbors

    @property
    def neighborLocation(self):
        """
        Yields the coordinates of neighboring cells
        """
        x,y = self.location
        yield (x - 1, y - 1)
        yield (x, y - 1)
        yield (x + 1, y - 1)
        yield (x - 1, y)
        yield (x + 1, y)
        yield (x - 1, y + 1)
        yield (x, y + 1)
        yield (x + 1, y + 1)

    def update(self):
        """

        Updates the cell's live neighbor count and increments
        the cells age if it is alive.
        """

        self.aliveNeighbors = sum(self.neighbors)
        self.age +=1

    def decideLife(self):
        """
        Determines a cell's new state based on the number of alive neighbors
        """

        if not self.alive and self.aliveNeighbors in self.alive_rule:
            self.alive = True
            self.age = 1
            return

        if self.alive and self.aliveNeighbors in self.death_rule:
            self.alive = False
            self.age = 0
            return

        self.age += 1

    def __add__(self,other):
        """

        :param other: Cell object
        :return: self.alive + other.alive
        """
        try:
            return self.alive + other.alive
        except AttributeError as e:
            return self.__radd__(other)

    def __radd__(self,other):
        """

        :return: other + self.alive
        """

        return other + self.alive




