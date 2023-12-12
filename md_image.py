from md_description import MDDescriptionTree


class ImageAttributes:
    def __init__(self, img_data):
        self.type = img_data[0]
        self.MIME_string = img_data[1]
        self.desc_string = img_data[2]
        self.width = img_data[3]
        self.height = img_data[4]
        self.color_depth = img_data[5]
        self.color_number = img_data[6]

    def __len__(self):
        return len(self.MIME_string) + len(self.desc_string) + self.width * self.height * (self.color_depth // 8)
    
    def __str__(self):
        result = ""

        result += "Type: {self.type}\n".format()
        result += "MIME: {self.MIME_string}\n".format()
        result += "Description: {self.desc_string}\n".format()
        result += "Width: {self.width}\n".format()
        result += "Height: {self.height}\n".format()
        result += "Color depth: {self.color_depth}\n".format()
        result += "Color number: {self.color_number}".format()

        return result


class MDBlockImage(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)

        self.attrs = None

    def add_content(self, img_data):
        self.attrs = ImageAttributes(img_data)

    def get_attrs(self):
        return self.attrs
    
    def check_for_change(self, new_value):
        return len(new_value) - len(self.attrs)
    
    def change_description(self, new_image, l_diff):
        *new_img_attrs, new_img_data = new_image
        local_changes = []

        if l_diff != 0:
            s, l = self.entries[1].entries[10].get_range()
            padding_index = self.parent.padding_block_idx
            dir_ = 1 if padding_index > self.parent.img_block_idx else -1
            if dir_ == 1:
                s0 = s + l
                f0 = self.parent.entries[padding_index].entries[1].get_range()[0] - 1 # shit
            else:
                s0 = s - 1
                f0 = self.parent.entries[padding_index + 1].get_range()[0] # even more shit
                
            local_changes.append((s0, f0, l_diff, dir_)) # shift bytes

            self.entries[1].entries[10].change_length(l_diff)

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
