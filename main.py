from track_editor import TrackEditor

if __name__ == "__main__":
    with TrackEditor("Funeralopolis.flac") as te:
        print(len(te.track_contents))
        while True:
            command = input(">")

            if command == "end":
                break

            if command == "show":
                te.show_description()

            if command.isdigit():
                te._look_block(int(command))     

            if command == "comments":
                te.print_comments()

            if command == "picture":
                te.print_picture_attributes()

