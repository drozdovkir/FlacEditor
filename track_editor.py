from md_processor import process_md, write_content, shift_bytes, read_image


class TrackEditor:
    def __init__(self, track_path):
        self.track_path = track_path
        self.track_handler = None
        self.track_contents = None
        self.md_description = None

        self.track_handler = open(self.track_path, "r+b")
        self.md_description, self.track_contents = process_md(self.track_handler)
        self.track_handler.close()

    @property
    def comments(self):
        return self.md_description.get_comment()
    
    def space(self):
        return self.md_description.get_available_space()
    
    def _change_bytes(self, changes):
        for change in changes:
            if change[3] == 1 or change[3] == -1:
                shift_bytes(self.track_contents, *change)
            else:
                write_content(self.track_contents, *change)

    # for debugging
    def _look_bytes(self, start, finish):
        b2 = self.track_contents[start:finish]
        print(b2)

    # for debugging
    def _look_block(self, index):
        s, l = self.md_description.entries[index].get_range()
        self._look_bytes(s, s + l)

    # for debugging
    def _check_correctness(self, blocks):
        if not self.md_description._check_correctness():
            print("metadata description tree is not correct")
        
        new_blocks = self._make_snapshot()

        for i, block in enumerate(blocks):
            print(str(i) + ": " + str(block == new_blocks[i]))

    # for debugging
    def _make_snapshot(self):
        result = []
        for block in self.md_description.entries:
            s, l = block.get_range()
            result.append(self.track_contents[s:s+l])
        return result

    def edit_field(self, field, new_value):
        # blocks = self._make_snapshot()

        if field == "cover":
            new_value = read_image(new_value)

        changes = self.md_description.change_description(field.upper(), new_value)
        if len(changes) == 0:
            print("requested change cannot be performed")
            return
        self._change_bytes(changes)

        #self._check_correctness(blocks)
    
    def show_description(self):
        print(self.md_description)

    def print_comments(self, *fields):
        fields = tuple(map(lambda elem: elem.upper(), fields))
        comments = self.md_description.get_comment(*fields)
        
        for comment, comment_value in comments.items():
            print(comment + ": ", end='')
            if comment_value is not None:
                print(comment_value)
            else:
                print("is not in metadata")

    def print_image_attributes(self):
        img_attrs = self.md_description.get_img_attrs()
        
        for key, value in img_attrs.items():
            print(key + ": " + value)

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is not None:
            print(exc_type)
            print(exc_value)
            print(exc_tb)
        self.track_handler.close()
        return True

if __name__ == "__main__":
    with TrackEditor("Funeralopolis.flac") as te:
        te.show_description()
        print("\n\n")

        te.print_comments("artist", "album", "haha")
        print("\n\n")
        te.edit_field("haha", "opa")

        te.print_comments("artist", "album", "haha")
