from md_description import MDDescriptionTree


class MD(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)

        self.padding_block_idx = -1
        self.vorbis_block_idx = -1
        self.img_block_idx = -1

    def get_comment(self, *args):
        return self.entries[self.vorbis_block_idx].get_comment(*args)
    
    def get_img_attrs(self):
        return self.entries[self.img_block_idx].get_attrs()
    
    def change_description(self, field, new_value):
        match field:
            case "cover":
                if self.img_block_idx == -1:
                    changes = self.create_image_block(new_value)
                    return changes
                if new_value is None:
                    changes = self.remove_image_block()
                    return changes
                idx = self.img_block_idx
            case _:
                idx = self.vorbis_block_idx
        
        l_diff = self.entries[idx].check_for_change(field, new_value)
        available_space = self.entries[self.padding_block_idx].space

        if l_diff > available_space:
            return []

        # changing the value of the field in the description should go first
        # so all start and length attributes have consistent values
        # and first change is byteshift
        changes1 = self.entries[idx].change_description(field, new_value, l_diff)    
        changes2 = self.entries[self.padding_block_idx].change_description(l_diff)

        return changes1 + changes2
    
    def create_image_block(self, img_data):
        pass
        # l_diff = 36 + len(img_data[1]) + len(img_data[2]) + len(img_data[7])
        # available_space = self.entries[self.padding_block_idx].space
        # if l_diff > available_space:
        #     return []
        
        # s = self.entries[self.padding_block_idx].start
        # changes = []

        # s0, l0 = self.entries[self.padding_block_idx].entries[0].get_range()
        # self.entries[self.padding_block_idx].start += l_diff
        # changes.append((s0, s0 + l0 - 1, l_diff, 1)) # shift bytes

        # img_block = None

        # header = MDBlockHeader()

        # block_type = MDDescriptionTree(length=1)
        # header.add_child(block_type)
        # changes.append((s, 1, 6, "be"))
        # s += 1

        # block_length = MDDescriptionTree(length=3)
        # header.add_child(block_length)
        # changes.append((s, 3, l_diff - 4, "be"))
        # s += 3

        # body = MDBlockData()

        # img_type = MDDescriptionTree(length=4)
        # body.add_child(img_type)
        # changes.append((s, 4, img_data[0], "be"))
        # s += 4

        # MIME_string_length = MDDescriptionTree(length=4)
        # body.add_child(MIME_string_length)
        # changes.append((s, 4, len(img_data[1]), "be"))
        # s += 4

        # MIME_string = MDDescriptionTree(length=len(img_data[1]))
        # body.add_child(MIME_string)
        # changes.append((s, len(img_data[1]), img_data[1], "s"))
        # s += len(img_data[1])

        # desc_string_length = MDDescriptionTree(length=4)
        # body.add_child(desc_string_length)
        # changes.append((s, 4, len(img_data[2]), "be"))
        # s += 4

        # desc_string = MDDescriptionTree(length=len(img_data[2]))
        # body.add_child(desc_string)
        # changes.append((s, len(img_data[2]), img_data[2], "s"))
        # s += len(img_data[2])

        # width = MDDescriptionTree(length=4)
        # body.add_child(width)
        # changes.append((s, 4, img_data[3], "be"))
        # s += 4

        # height = MDDescriptionTree(length=4)
        # body.add_child(height)
        # changes.append((s, 4, img_data[4], "be"))
        # s += 4

        # color_depth = MDDescriptionTree(length=4)
        # body.add_child(color_depth)
        # changes.append((s, 4, img_data[5], "be"))
        # s += 4

        # color_number = MDDescriptionTree(length=4)
        # body.add_child(color_number)
        # changes.append((s, 4, img_data[6], "be"))
        # s += 4

        # data_length = MDDescriptionTree(length=4)
        # body.add_child(data_length)
        # changes.append((s, 4, len(img_data[7]), "be"))
        # s += 4

        # data = MDDescriptionTree(length=len(img_data[7]))
        # body.add_child(data)
        # changes.append((s, len(img_data[7]), img_data[7]))
        # s += len(img_data[7])

        # img_block.add_child(header)
        # img_block.add_child(body)

        # img_block.add_content(img_data)

        # self.entries[self.padding_block_idx].insert_node(img_block)
        
        # changes += self.entries[self.padding_block_idx].change_description(l_diff)

        # return changes

    def remove_image_block(self):
        s, l = self.entries[self.img_block_idx].get_range()
        changes = []
        padding_index = self.padding_block_idx
        dir_ = 1 if padding_index > self.img_block_idx else -1
        if dir_ == 1:
            s0 = s + l
            f0 = self.entries[padding_index].entries[1].get_range()[0] - 1 # shit
        else:
            s0 = s - 1
            f0 = self.entries[padding_index + 1].get_range()[0] # even more shit
                
        changes.append((s0, f0, -l, dir_)) # shift bytes

        self.entries[self.img_block_idx].remove_node()

        # pls kill me
        if self.img_block_idx < self.padding_block_idx:
            self.padding_block_idx -= 1
        if self.img_block_idx < self.vorbis_block_idx:
            self.vorbis_block_idx -= 1

        changes += self.entries[self.padding_block_idx].change_description(-l)

        self.img_block_idx = -1

        print("done")
        return changes
