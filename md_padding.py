from md_description import MDDescriptionTree


class MDBlockPadding(MDDescriptionTree):
    def __init__(self, start_=0, length_=0):
        super().__init__(start=start_, length=length_)

        self.space = 0

    def add_content(self, space):
        self.space = space
        self.is_padding = True

    def change_description(self, l_diff):
        if l_diff == 0:
            return []
        
        self.space -= l_diff
        s, l = self.entries[0].entries[1].get_range()

        return [(s, l, self.space, "be")]
    