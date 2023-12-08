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
            self.comments[field] = comment_info
            i += 2
        
        self.list_length_field = self.entries[1].entries[2]
    
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
            return len(new_value) + 4
        
        old_value = old_value.value
        
        return len(new_value) - len(old_value)
    
    def change_description(self, field, new_value, padding_index, l_diff, dir_):
        if field not in self.comments.keys():
            changes = self.create_comment_node(field, new_value, padding_index, l_diff, dir_)
            return changes
        
        self.comments[field] = VorbisCommentInfo(new_value, 
                                                       self.comments[field].node, 
                                                       self.comments[field].length_node)
        
        new_string = field + "=" + new_value
        new_block_length = self.entries[1].length + l_diff

        local_changes = []
        
        if l_diff != 0:
            s, l = self.comments[field].node.get_range()
            if dir_ == 1:
                s0 = s + l
                f0 = self.parent.entries[padding_index].entries[1].get_range()[0] - 1 # shit
            else:
                s0 = s - 1
                f0 = self.parent.entries[padding_index + 1].get_range()[0] # even more shit
                
            local_changes.append((s0, f0, l_diff, dir_))           # shift bytes

            self.comments[field].node.change_length(padding_index, l_diff, dir_)

            s2, l2 = self.comments[field].length_node.get_range()
            local_changes.append((s2, l2, len(new_string), "le"))  # rewrite length of the comment

            s3, l3 = self.entries[0].entries[1].get_range()
            local_changes.append((s3, l3, new_block_length, "be")) # rewrite length of the block


        s1, l1 = self.comments[field].node.get_range()
        local_changes.append((s1, l1, new_string, "s"))        # rewrite comment

        return local_changes
    
    def create_comment_node(self, field, value, padding_index, l_diff, dir_):
        new_string = field + "=" + value

        local_changes = []

        s, l = self.entries[1].entries[-1].get_range()
        if dir_ == 1:
            s0 = s + l
            f0 = self.parent.entries[padding_index].entries[1].get_range()[0] - 1 # shit
        else:
            s0 = s - 1
            f0 = self.parent.entries[padding_index + 1].get_range()[0] # even more shit
        local_changes.append((s0, f0, l_diff, dir_)) # shift bytes
        
        length = MDDescriptionTree(length=4)
        local_changes.append((s + l, 4, len(new_string), "le")) # add length of comment

        comment = MDDescriptionTree(length=len(new_string))
        local_changes.append((s + l + 4, len(new_string), new_string, "s")) # add comment

        node = self.list_length_field

        node.insert_node(comment)
        node.insert_node(length)

        s1, l1 = node.get_range()
        local_changes.append(s1, l1, len(self.comments.keys()) + 1, "le") # change number of comments

        s2, l2 = self.entries[0].entries[1].get_range()
        new_block_length = self.entries[1].length + len(new_string)
        local_changes.append((s2, l2, new_block_length, "be")) # change block length

        return local_changes

    def remove_comment_node(self, field, padding_index, dir_):
        node = self.comments[field].node
        length_node = self.comments[field].length_node
        
        node.change_length(padding_index, -node.length, dir_)
        length_node.change_length(padding_index, -length_node.length, dir_)

        local_changes = []

        node.remove_node()
        length_node.remove_node()

        local_changes.append(()) # shift bytes
        local_changes.append(()) # change number of comments

        return local_changes
