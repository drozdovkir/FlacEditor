from track_editor import TrackEditor

if __name__ == "__main__":
    with TrackEditor("Dark Fantasy.flac") as te:
        print(len(te.track_contents))
        print(te.md_description.length)

        while True:
            command = input(">")

            if command == "end":
                break

            if command == "show":
                te.show_description()

            if command == "change":
                te.edit_field("ARTIST", "ME")
                te.edit_field("TITLE", "x")
                te.edit_field("ALBUM", "WOW")

            if command.isdigit():
                te._look_block(int(command))     

            if command == "comments":
                te.print_comments()

            if command == "image":
                te.print_image_attributes()

