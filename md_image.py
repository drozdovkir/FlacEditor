from md_description import MDDescriptionTree, MDBlockHeader, MDBlockData
from collections import namedtuple

ImageAttributeInfo = namedtuple("ImageAttributeInfo", "value node length_node")


class MDBlockImage(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)

        self.attrs = {}

    def add_content(self, img_data):
        self.attrs = img_data

    def get_attrs(self):
        return self.attrs
    
    def check_for_change(self, new_value):
        return ((len(new_value["MIME_string"]) - len(self.attrs["MIME_string"])) +
               (len(new_value["description_string"]) - len(self.attrs["description_string"])) +
               (new_value["width"] * new_value["height"] * (new_value["color_depth"] // 8) - self.attrs["width"] * self.attrs["height"] * (self.attrs["color_depth"] // 8)))
    
    def change_value(self, attr, value):
        local_changes = []

        match attr:
            case "MIME_string" | "description_string":
                s0, f0, dir_ = self.attrs[attr].node.get_orientation()
                local_changes.append((s0, f0, len(value) - len(self.attrs.get(attr)), dir_)) # shift bytes
                
                self.attrs[attr] = ImageAttributeInfo(value, self.attrs[attr].node, self.attrs[attr].length_node)
                
                self.attrs[attr].node.change_length(len(value) - len(self.attrs.get(attr)))

                s1, l1 = self.attrs[attr].node.get_range()
                local_changes.append((s1, l1, value, "s")) # change string

                s2, l2 = self.attrs[attr].length_node.get_range()
                local_changes.append((s2, l2, len(value), "be")) # change length of string

            case _:
                self.attrs[attr] = ImageAttributeInfo(value, self.attrs[attr].node, self.attrs[attr].length_node)
                s, l = self.attrs[attr].node.get_range()
                local_changes.append((s, l, value, "be")) # change value
        
        return local_changes
    
    def change_description(self, _, new_image, l_diff):
        new_img_attrs, new_img_data = new_image
        local_changes = []

        new_length = self.entries[1].length + l_diff

        for attr, value in new_img_attrs.items():
            if value != self.attrs[attr].value:
                local_changes += self.change_value(attr, value)
    
        s1, l1 = self.entries[1].entries[10].get_range()
        local_changes.append(s1, l1, new_img_data.data) # change image data

        s2, l2 = self.entries[0].entries[1].get_range()
        local_changes.append(s2, l2, new_length, "be") # change block length

        return local_changes
    
    def create_from_image(self, img_attrs):
        header = MDBlockHeader()
        bt = MDDescriptionTree(length=1)
        bl = MDDescriptionTree(length=3)
        header.add_child(bt)
        header.add_child(bl)

        body = MDBlockData()

        for attr in ["type", "MIME_string", "description_string", "width", "height", "color_depth", "color_number"]:
            value = img_attrs[attr]
            print(value)
            match attr:
                case "MIME_string" | "description_string":
                    new_length_node = MDDescriptionTree(length=4)
                    new_node = MDDescriptionTree(length=len(value))

                    self.attrs[attr] = ImageAttributeInfo(value, new_node, new_length_node)

                    body.add_child(new_length_node)
                    body.add_child(new_node)

                case _:
                    new_node = MDDescriptionTree(length=4)
                    self.attrs[attr] = ImageAttributeInfo(value, new_node, None)
                    body.add_child(new_node)
        
        new_node = MDDescriptionTree(length=4)
        img_size = self.attrs["width"].value * self.attrs["height"].value * self.attrs["color_depth"].value
        new_node_1 = MDDescriptionTree(length=img_size)
        body.add_child(new_node)
        body.add_child(new_node_1)

        self.add_child(header)
        self.add_child(body)