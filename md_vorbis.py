from md_description import MDDescriptionTree
from collections import namedtuple

VorbisCommentInfo = namedtuple("VorbisCommentInfo", "value node length_node")


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
            self.comments[field.upper()] = comment_info
            i += 2
        
        self.list_length_field = self.entries[1].entries[2]
    
    def get_comment(self, *comments):
        if comments == ():
            return {field : info.value for field, info in self.comments.items()}
        
        return {field : (self.comments.get(field).value if field in self.comments.keys() else None) for field in comments}
    
    def check_for_change(self, field, new_value):
        old_value = self.comments.get(field)
        
        new_length = old_length = len(field) + 5

        if old_value is None:
            old_length = 0
        else:
            old_length += len(old_value.value)
        
        if new_value is None:
            new_length = 0
        else:
            new_length += len(new_value)
        
        return new_length - old_length
    
    def change_description(self, field, new_value, l_diff):
        if new_value is None:
            changes = self.remove_comment_node(field, l_diff)
            return changes
        
        if field not in self.comments.keys():
            changes = self.create_comment_node(field, new_value, l_diff)
            return changes
        
        if new_value == self.comments[field].value:
            return []
        
        self.comments[field] = VorbisCommentInfo(new_value, 
                                                       self.comments[field].node, 
                                                       self.comments[field].length_node)
        
        new_string = field + "=" + new_value
        new_block_length = self.entries[1].length + l_diff

        local_changes = []
        
        if l_diff != 0:
            s0, f0, dir_ = self.comments[field].node.get_orientation()  
            local_changes.append((s0, f0, l_diff, dir_))           # shift bytes

            self.comments[field].node.change_length(l_diff)

            s2, l2 = self.comments[field].length_node.get_range()
            local_changes.append((s2, l2, len(new_string), "le"))  # rewrite length of the comment

            s3, l3 = self.entries[0].entries[1].get_range()
            local_changes.append((s3, l3, new_block_length, "be")) # rewrite length of the block


        s1, l1 = self.comments[field].node.get_range()
        local_changes.append((s1, l1, new_string, "s"))        # rewrite comment

        return local_changes
    
    def create_comment_node(self, field, value, l_diff):
        new_value = field + "=" + value

        local_changes = []

        s0, f0, dir_ = self.list_length_field.get_orientation()
        local_changes.append((s0, f0, l_diff, dir_)) # shift bytes
        
        node = self.list_length_field

        length = MDDescriptionTree(length=4)
        comment = MDDescriptionTree(length=len(new_value))

        # the order matters
        node.insert_node(comment)
        node.insert_node(length)

        self.comments[field] = VorbisCommentInfo(value, comment, length)
        
        s1, l1 = length.get_range()
        local_changes.append((s1, l1, len(new_value), "le")) # add length of comment

        s2, l2 = comment.get_range()
        local_changes.append((s2, l2, new_value, "s")) # add comment

        s3, l3 = node.get_range()
        local_changes.append((s3, l3, len(self.comments.keys()), "le")) # change number of comments

        s4, l4 = self.entries[0].entries[1].get_range()
        new_block_length = self.entries[1].length + len(new_value)
        local_changes.append((s4, l4, new_block_length, "be")) # change block length

        return local_changes

    def remove_comment_node(self, field, l_diff):
        if field not in self.comments.keys():
            return [(0, 1, 0, 1),] # basically 'do nothing' change to distinguish this situation
                                # from that of inability to make a change
        node = self.comments[field].node
        length_node = self.comments[field].length_node

        self.comments.pop(field)

        local_changes = []

        s0, f0, dir_ = length_node.get_orientation()
        _, l2 = node.get_range()

        if dir_ == 1:
            f += l2

        local_changes.append((s0, f0, l_diff, dir_)) # shift bytes

        node.remove_node()
        length_node.remove_node()

        s, l = self.list_length_field.get_range()
        local_changes.append((s, l, len(self.comments.keys()), "le")) # change number of comments

        return local_changes
