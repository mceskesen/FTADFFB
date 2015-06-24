'''
Created 23 March 2015

@author: Morten Chabert Eskesen
'''

import collections


"""This module implements an union find or disjoint set data structure.

An union find data structure can keep track of a set of elements into a number
of disjoint (nonoverlapping) subsets. That is why it is also known as the
disjoint set data structure. Mainly two useful operations on such a data
structure can be performed. A *find* operation determines which subset a
particular element is in. This can be used for determining if two
elements are in the same subset. An *union* Join two subsets into a
single subset.

The complexity of these two operations depend on the particular implementation.
It is possible to achieve constant time (O(1)) for any one of those operations
while the operation is penalized. A balance between the complexities of these
two operations is desirable and achievable following two enhancements:

1.  Using union by rank -- always attach the smaller tree to the root of the
    larger tree.
2.  Using path compression -- flattening the structure of the tree whenever
    find is used on it.

complexity:
    * find -- :math:`O(\\alpha(N))` where :math:`\\alpha(n)` is
      `inverse ackerman function
      <http://en.wikipedia.org/wiki/Ackermann_function#Inverse>`_.
    * union -- :math:`O(\\alpha(N))` where :math:`\\alpha(n)` is
      `inverse ackerman function
      <http://en.wikipedia.org/wiki/Ackermann_function#Inverse>`_.

"""


class UF:
    """An implementation of union find data structure.
    It uses weighted quick union by rank with path compression.
    """

    def __init__(self, N):
        """Initialize an empty union find object with N items.

        Args:
            N: Number of items in the union find object.
        """

        self._id = list(range(N))
        self._count = N
        self._rank = [0] * N

    def find(self, p):
        """Find the set identifier for the item p."""

        id = self._id
        while p != id[p]:
            id[p] = id[id[p]]   # Path compression using halving.
            p = id[p]
        return p

    def count(self):
        """Return the number of items."""

        return self._count

    def connected(self, p, q):
        """Check if the items p and q are on the same set or not."""

        return self.find(p) == self.find(q)

    def union(self, p, q):
        """Combine sets containing p and q into a single set."""

        id = self._id
        rank = self._rank

        i = self.find(p)
        j = self.find(q)
        if i == j:
            return

        self._count -= 1
        if rank[i] < rank[j]:
            id[i] = j
        elif rank[i] > rank[j]:
            id[j] = i
        else:
            id[j] = i
            rank[i] += 1

    def __str__(self):
        """String representation of the union find object."""
        return " ".join([str(x) for x in self._id])

    def __repr__(self):
        """Representation of the union find object."""
        return "UF(" + str(self) + ")"


class OrderedSet(collections.Set):
    '''
    Ordered Set data structure
    Introduced to ensure deterministic output from list scheduler.
    '''
    
    def __init__(self, iterable = None):
        '''
        Constructor
        '''
        self.head = None
        self.tail = None
        self.map = {}                           # key --> [key, prev, next]
        if iterable is not None:
            for each in iterable:
                self.add(each)
            
    def add(self, key):
        '''
        Add key to set.
        '''
        if key not in self.map:
            new = self.map[key] = [key, self.tail, None]
            if not self.head: # First element in list
                self.head = new
                self.tail = new
            else:
                self.tail[2] = new
            self.tail = new
            
    def remove(self, key):
        '''
        Remove key from set
        '''
        if key in self.map:
            current = self.map[key]
            prev = current[1]
            next_ = current[2]
            
            if self.tail != current:
                next_[1] = prev
            else:
                self.tail = prev
                
            if self.head != current:
                prev[2] = next_
            else:
                self.head = next_
                
            del self.map[key]
    
    def get_head(self):
        '''
        Return first element.
        '''
        if self.head:
            return self.head[0]
        else:
            return None

    def get_tail(self):
        '''
        Return last element.
        '''
        if self.tail:
            return self.tail[0]
        else:
            return None
        
    def copy(self):
        s = OrderedSet()
        for each in self:
            s.add(each)
        return s
        
    def __len__(self):
        return len(self.map)
            
    def __contains__(self, key):
        return key in self.map
        
    def __iter__(self):
        current = self.head
        while current:
            yield current[0]
            current = current[2]
            
    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, list(self))
