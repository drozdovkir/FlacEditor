from utils import *
from collections import namedtuple

VorbisCommentInfo = namedtuple("VorbisCommentInfo", "value node length_node")


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
    
    def change_length(self, padding_index, l_diff, dir_):
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
        if dir_ == -1:                  # uuuuuuuughhhh
            prev_node.start -= l_diff

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
    

class MD(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)

        self.padding_block_idx = 0
        self.vorbis_block_idx = 0
        self.pic_block_idx = 0

    def get_comment(self, *args):
        return self.entries[self.vorbis_block_idx].get_comment(*args)
    
    def get_pic_attrs(self):
        return self.entries[self.pic_block_idx].get_attrs()
    
    def change_description(self, field, new_value):
        match field:
            case "ARTIST" | "TITLE" | "ALBUM" | "GENRE" | "YEAR" | "TRACKNUMBER":
                idx = self.vorbis_block_idx
            case "cover":
                idx = self.pic_block_idx

        l_diff = self.entries[idx].check_for_change(field, new_value)
        available_space = self.entries[self.padding_block_idx].space

        if l_diff > available_space:
            return []
        
        if idx < self.padding_block_idx:
            dir_ = 1
        else:
            dir_ = -1

        # changing the value of the field in the description should go first
        # so all start and length attributes have consistent values
        # and first change is byteshift
        changes1 = self.entries[idx].change_description(field, new_value, self.padding_block_idx, l_diff, dir_)    
        changes2 = self.entries[self.padding_block_idx].change_description(l_diff)

        return changes1 + changes2


class MDBlockStreamInfo(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)


class MDBlockPadding(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)

        self.space = 0

    def add_content(self, space):
        self.space = space

    def change_description(self, l_diff):
        self.space -= l_diff

        self.entries[1].length -= l_diff

        s, l = self.entries[0].entries[1].get_range()

        return [(s, l, self.space, "be")]


class MDBlockApplication(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)


class MDBlockSeekTable(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)


class MDBlockVorbisComment(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)

        self.list_length_field = None
        self.comments = {} # contains values, references to comment's node, node with length of comment

    def add_content(self, comments):
        i = 3
        for comment in comments:
            field, value = comment.split('=')
            comment_info = VorbisCommentInfo(value, self.entries[1].entries[i + 1], self.entries[1].entries[i])
            self.comments[field] = comment_info
            i += 2
    
    def get_comment(self, *comments):
        if comments == ():
            return self.comments
        
        result = {}
        for comment_field in comments:
            result[comment_field] = self.comments.get(comment_field)
        
        return result
    
    def check_for_change(self, field, new_value):
        old_value = self.comments.get(field)

        if old_value is None:
            raise Exception()
        
        old_value = old_value.value
        
        return len(new_value) - len(old_value)
    
    def change_description(self, field, new_value, padding_index, l_diff, dir_):
        self.comments[field] = VorbisCommentInfo(new_value, 
                                                       self.comments[field].node, 
                                                       self.comments[field].length_node)
        
        s, l = self.comments[field].node.get_range()
        if dir_ == 1:
            s0 = s + l
            f0 = self.parent.entries[padding_index].entries[1].get_range()[0] - 1 # shit
        else:
            s0 = s - 1
            f0 = self.parent.entries[padding_index + 1].get_range()[0] # even more shit

        new_string = field + "=" + new_value
        new_block_length = self.entries[1].length + l_diff

        self.comments[field].node.change_length(padding_index, l_diff, dir_)

        local_changes = []

        s1, l1 = self.comments[field].node.get_range()

        if l_diff == 0:
            return [(s1, l1, new_string, "s")]
        
        s2, l2 = self.comments[field].length_node.get_range()
        s3, l3 = self.entries[0].entries[1].get_range()

        local_changes.append((s0, f0, l_diff, dir_))           # shift bytes
        local_changes.append((s1, l1, new_string, "s"))        # rewrite comment
        local_changes.append((s2, l2, len(new_string), "le"))  # rewrite length of the comment
        local_changes.append((s3, l3, new_block_length, "be")) # rewrite length of the block

        return local_changes


class MDBlockCuesheet(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)


class MDBlockPicture(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)

        self.type = -1
        self.width = -1
        self.height = -1
        self.color_depth = -1
        self.color_number = -1

    def add_content(self, pic_data):
        self.type = pic_data[0]
        self.width = pic_data[1]
        self.height = pic_data[2]
        self.color_depth = pic_data[3]
        self.color_number = pic_data[4]

    def get_attrs(self):
        result = {}

        result["type"] = str(self.type)
        result["width"] = str(self.width)
        result["height"] = str(self.height)
        result["color depth"] = str(self.color_depth)
        result["color number"] = str(self.color_number)

        return result


class MDBlockHeader(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)


class MDBlockData(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)
