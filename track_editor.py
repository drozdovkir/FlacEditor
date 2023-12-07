from md_processor import process_md, write_content, shift_bytes


class TrackEditor:
    def __init__(self, track_path):
        self.track_path = track_path
        self.track_handler = None
        self.track_contents = None
        self.md_description = None

    def __enter__(self):
        self.track_handler = open(self.track_path, "r+b")

        self.track_contents = bytearray(self.track_handler.read())
        self.md_description = process_md(self.track_contents)

        return self
    
    def _change_bytes(self, changes):
        for change in changes:
            if change[3] == 1 or change[3] == -1:
                shift_bytes(self.track_contents, *change)
            else:
                write_content(self.track_contents, *change)

    def _look_bytes(self, start, finish):
        print(self.track_contents[start:finish])

    def _look_block(self, index):
        s, l = self.md_description.entries[index].get_range()
        self._look_bytes(s, s + l)

    def edit_field(self, field, new_value):
        changes = self.md_description.change_description(field, new_value)
        if len(changes) == 0:
            print("requested change cannot be performed")
            return
        self._change_bytes(changes)
    
    def show_description(self):
        print(self.md_description)

    def print_comments(self, *comments):
        comments = self.md_description.get_comment(*comments)
        
        for comment, comment_value in comments.items():
            print(comment + ": ", end='')
            if comment_value is not None:
                print(comment_value.value)
            else:
                print("is not in metadata")

    def print_picture_attributes(self):
        pic_attrs = self.md_description.get_pic_attrs()
        
        for key, value in pic_attrs.items():
            print(key + ": " + value)

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is not None:
            print(exc_type)
            print(exc_value)
        self.track_handler.close()
        return True


if __name__ == "__main__":
    with TrackEditor("Dark Fantasy.flac") as te:
        te.show_description()
        te.print_comments()
        te.print_picture_attributes()
        #print(te.md_description.entries[te.md_description.vorbis_block_idx].comments)
