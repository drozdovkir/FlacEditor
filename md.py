from md_description import MDDescriptionTree
from md_image import MDBlockImage


class MD(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)

        self.padding_block_idx = -1
        self.vorbis_block_idx = -1
        self.img_block_idx = -1

    def get_available_space(self):
        return self.entries[self.padding_block_idx].space

    def get_comment(self, *args):
        return self.entries[self.vorbis_block_idx].get_comment(*args)
    
    def get_img_attrs(self):
        return self.entries[self.img_block_idx].get_attrs()
    
    def change_description(self, field, new_value):
        match field:
            case "COVER":
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
    
    def create_image_block(self, image):
        l_diff = 36 + len(image[0]["MIME_string"]) + len(image[0]["description_string"]) + len(image[1])
        available_space = self.entries[self.padding_block_idx].space
        if l_diff > available_space:
            return []
        
        image_block = MDBlockImage()
        image_block.create_from_image(image[0])
        self.entries[self.padding_block_idx].insert_node(image_block)
        self.img_block_idx = self.padding_block_idx + 1

        changes1 = image_block.change_description(None, image, l_diff)
        changes2 = self.entries[self.padding_block_idx].change_description(l_diff)

        return changes1 + changes2

    def remove_image_block(self):
        changes = []

        s0, f0, dir_ = self.entries[self.img_block_idx].get_orientation()
        l = self.entries[self.img_block_idx].length        
        changes.append((s0, f0, -l, dir_)) # shift bytes

        self.entries[self.img_block_idx].remove_node()

        # pls kill me
        if self.img_block_idx < self.padding_block_idx:
            self.padding_block_idx -= 1
        if self.img_block_idx < self.vorbis_block_idx:
            self.vorbis_block_idx -= 1

        changes += self.entries[self.padding_block_idx].change_description(-l)

        self.img_block_idx = -1

        return changes
