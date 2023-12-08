from utils import *


class MDDescriptionTree:
    def __init__(self, start=0, length=0):
        self.start = start
        self.length = length
        self.entries = []
        self.parent = None
    
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
    def insert_node(self, new_node, padding_index, dir_):
        p_node = self.parent

        idx = p_node.entries.index(self)
        p_node.entries.insert(idx, new_node)
        new_node.start = self.start
        new_node.parent = p_node

        l = new_node.length
        new_node.length = 0

        new_node.change_length(padding_index, l, dir_)
    
    def change_length(self, padding_index, l_diff, dir_):
        if l_diff == 0:
            return
        
        cur_node = self
        prev_node = None

        # outer loop for traversing levels of the tree starting with the lowest
        # up to the second layer where block nodes are situated
        while cur_node.parent is not None:

            # if node is a leaf (can only happen on the first iteration)
            if len(cur_node.entries) == 0:
                prev_node = cur_node
                cur_node = cur_node.parent
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

    def remove_node(self, padding_index, dir_):
        p_node = self.parent

        self.change_length(padding_index, -self.length, dir_)

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
