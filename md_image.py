from md_description import MDDescriptionTree


class MDBlockImage(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)

        self.type = -1
        self.MIME_string = None
        self.desc_string = None
        self.width = -1
        self.height = -1
        self.color_depth = -1

    def add_content(self, img_data):
        self.type = img_data[0]
        self.MIME_string = img_data[1]
        self.desc_string = img_data[2]
        self.width = img_data[3]
        self.height = img_data[4]
        self.color_depth = img_data[5]

    def get_attrs(self):
        result = {}

        result["type"] = str(self.type)
        result["MIME"] = self.MIME_string
        result["description"] = self.desc_string
        result["width"] = str(self.width)
        result["height"] = str(self.height)
        result["color depth"] = str(self.color_depth)

        return result
    
    def check_for_change(self, new_value):
        return len(new_value) - self.width * self.height * (self.color_depth // 8)
    
    def change_description(self, new_img_data, padding_index, l_diff, dir_):
        local_changes = []

        if l_diff != 0:
            s, l = self.entries[1].entries[10].get_range()
            if dir_ == 1:
                s0 = s + l
                f0 = self.parent.entries[padding_index].entries[1].get_range()[0] - 1 # shit
            else:
                s0 = s - 1
                f0 = self.parent.entries[padding_index + 1].get_range()[0] # even more shit
                
            local_changes.append((s0, f0, l_diff, dir_)) # shift bytes

            self.entries[1].entries[10].change_length(padding_index, l_diff, dir_)

            s, l = self.entries[1].entries[9].get_range()
            local_changes.append((s, l, len(new_img_data.data), "be"))

        if self.type != new_img_data[0]:
            self.type = new_img_data[0]
            s, l = self.entries[1].entries[0].get_range()
            local_changes.append((s, l, self.type, "be"))

        if self.width != new_img_data[1]:
            self.width = new_img_data[1]
            s, l = self.entries[1].entries[5].get_range()
            local_changes.append((s, l, self.width, "be"))

        if self.height != new_img_data[2]:
            self.height = new_img_data[2]
            s, l = self.entries[1].entries[6].get_range()
            local_changes.append((s, l, self.height, "be"))

        if self.color_depth != new_img_data[3]:
            self.color_depth = new_img_data[3]
            s, l = self.entries[1].entries[7].get_range()
            local_changes.append((s, l, self.color_depth, "be"))

        s, l = self.entries[1].entries[10].get_range()
        local_changes.append(s, l, new_img_data.data)

        return local_changes
