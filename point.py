#this file contains the point (i.e. (x,y)) class

class Point:
    def __init__(self, xIn, yIn):
        self.x = xIn
        self.y = yIn
    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, val):
        self._x = val
    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, val):
        self._y = val

    def __eq__(self, other):
        if (self.x == other.x) and (self.y == other.y):
            return True
        return False
    def __ne__(self, other):
        if (self.x != other.x) or (self.y != other.y):
            return True
        return False
    def printStr(self):
        return f"({self.x}, {self.y})"

