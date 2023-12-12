from utils import *


class MDDescriptionTree:
    def __init__(self, start=0, length=0):
        self.start = start
        self.length = length
        self.entries = []
        self.parent = None
        self.is_padding = False
    
    # call only during the initial building of a tree
    def add_child(self, child_node):
        if len(self.entries) == 0:
            child_node.start = 0
        else:
            child_node.start = self.entries[-1].start + self.entries[-1].length
        
        child_node.parent = self
        self.entries.append(child_node)

        # keeping parent.l = sum child.l invariant
        # don't need to shift neighboring nodes because at the stage of building tree they don't exist yet
        cur_node = self
        while cur_node is not None:
            cur_node.length += child_node.length
            cur_node = cur_node.parent
    
    # call when tree is already built
    def insert_node(self, new_node):
        p_node = self.parent

        idx = p_node.entries.index(self)
        p_node.entries.insert(idx + 1, new_node)
        new_node.start = self.start + self.length
        new_node.parent = p_node

        l = new_node.length
        new_node.length = 0

        new_node.change_length(l)
    
    def change_length(self, l_diff):
        if l_diff == 0:
            return
        
        cur_node = self
        prev_node = None

        # outer loop for traversing levels of the tree starting with the lowest
        # up to the second layer where block nodes are situated
        entered = False
        while cur_node.parent is not None:

            # skip first iteration
            if not entered:
                prev_node = cur_node
                cur_node = cur_node.parent
                entered = True
                continue

            # inner loop for traversing children of a given node
            # because start attribute is relative changes propagate only to the right
            i = len(cur_node.entries) - 1
            while cur_node.entries[i] != prev_node:
                cur_node.entries[i].start += l_diff
                i -= 1
            prev_node.length += l_diff

            prev_node = cur_node
            cur_node = cur_node.parent
        
        # THIS WORKS SOMEHOW, DO NOT TOUCH
        dir_ = 1
        padding_index = -1
        for i, node in enumerate(cur_node.entries):
            if node.is_padding:
                padding_index = i
                dir_ *= dir_
            if node == prev_node:
                dir_ *= -1

        # loop for traversing block layer of the tree
        # same as the inner loop but traversing ends on padding block
        # and can go both directions
        i = padding_index if dir_ == 1 else padding_index + 1
        while cur_node.entries[i] != prev_node:
            cur_node.entries[i].start += l_diff * dir_ 
            i -= dir_
        cur_node.entries[padding_index].length -= l_diff
        cur_node.entries[padding_index].entries[1].length -= l_diff
        prev_node.length += l_diff
        if dir_ == -1:                  # uuuuuuuughhhh
            prev_node.start -= l_diff

    def remove_node(self):
        p_node = self.parent

        self.change_length(-self.length)

        p_node.entries.remove(self)

    def get_range(self):
        global_start = 0

        cur_node = self
        while cur_node is not None:
            global_start += cur_node.start
            cur_node = cur_node.parent

        return global_start, self.length
    
    def add_content(self, *args):
        return None
    
    # for pure diagnostic purposes
    def _check_correctness(self):
        if self.start < 0 or self.length < 0:
            print("start or length is scuffed")
            return False
        
        if len(self.entries) == 0:
            return True
        
        total_length = self.entries[0].length

        if self.entries[0].start != 0:
            print("doesn't start from 0")
            return False
        
        if not self.entries[0]._check_correctness():
            return False
        
        for i, entry in enumerate(self.entries[1:]):
            total_length += entry.length
            if entry.start != self.entries[i].start + self.entries[i].length:
                print("index {0}".format(i))
                print("doesn't start from last node")
                print(str(entry.start) + " != " + str(self.entries[i].start) + " + " + str(self.entries[i].length)) 
                return False
            
            if not entry._check_correctness():
                return False
        
        if total_length != self.length:
            print("total length is scuffed")
            return False
        
        return True
    
    def __str__(self):
        class_name = strip_class_name(str(type(self)))
        str_ = "{2}(start={0}, length={1})".format(self.start, self.length, class_name)
        for entry in self.entries:
            substrs = str(entry)
            substrs = substrs.split('\n')

            for substr_ in substrs:
                str_ += "\n----{0}".format(substr_)
        return str_
    

class MDBlockHeader(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)


class MDBlockData(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)


class MDBlockStreamInfo(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)


class MDBlockApplication(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)


class MDBlockSeekTable(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)


class MDBlockCuesheet(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)
