
class Partition(Set):

    def __init__(self, n):
        super(Partition, self).__init__(n)

    def find(self, obj):
        pass
    find = abstractmethod(find)

    def join(self, s, t):
        pass
    join = abstractmethod(join)

class PartitionAsForest(Partition):

    class PartitionTree(Set, Tree):

        def __init__(self, partition, item):
            super(PartitionAsForest.PartitionTree, self) \
                .__init__(partition._universeSize)
            self._partition = partition
            self._item = item
            self._parent = None
            self._rank = 0
            self._count = 1


class PartitionAsForest(Partition):

    def find(self, item):
        ptr = self._array[item]
        while ptr._parent is not None:
            ptr = ptr._parent
        return ptr

