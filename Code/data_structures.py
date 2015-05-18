'''
Created 23 March 2015

@author: Morten Chabert Eskesen
'''

import collections
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
