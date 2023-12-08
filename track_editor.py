from md_processor import process_md, write_content, shift_bytes
import imageio as iio


class TrackEditor:
    def __init__(self, track_path):
        self.track_path = track_path
        self.track_handler = None
        self.track_contents = None
        self.md_description = None

    def __enter__(self):
        self.track_handler = open(self.track_path, "r+b")

        self.md_description, self.track_contents = process_md(self.track_handler)

        self.track_handler.seek(0)

        return self
    
    def _change_bytes(self, changes):
        for change in changes:
            if change[3] == 1 or change[3] == -1:
                shift_bytes(self.track_contents, *change)
            else:
                write_content(self.track_contents, *change)

    def _look_bytes(self, start, finish):
        #self.track_handler.seek(start)
        #b1 = bytearray(self.track_handler.read(finish - start))
        b2 = self.track_contents[start:finish]
        # print(b1)
        print(b2)
        # print(b1 == b2)
        #self.track_handler.seek(0)

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

    def print_image_attributes(self):
        img_attrs = self.md_description.get_img_attrs()
        
        for key, value in img_attrs.items():
            print(key + ": " + value)

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is not None:
            print(exc_type)
            print(exc_value)
        self.track_handler.close()
        return True
