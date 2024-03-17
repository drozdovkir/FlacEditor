from dataclasses import dataclass
from utils import compare_strings
import msvcrt

from manager import Manager, AddTracks, RemoveTracks, AddMetadata, QuitApp
from command_interface import CommandInterface

ESC_CHARS = {"up": "\033[1A",
            "down": "\033[1B",
            "right": "\033[1C",
            "left": "\033[1D"}

PALLETE = {"no_color": "\033[37m",
           "blue_color": "\033[34m",
           "red_color": "\033[31m"}

WIDTH = 100
COMMAND_MODE = 0
NAVIGATION_MODE = 1


@dataclass
class Point:
    x: int
    y: int

    def __add__(self, rhs):
        return Point(self.x + rhs.x, self.y + rhs.y)
    
    def __sub__(self, rhs):
        return Point(self.x - rhs.x, self.y - rhs.y)


@dataclass
class Box:
    top: int
    right: int
    bottom: int
    left: int


manager = Manager()
ci = CommandInterface(manager)

cursor_pos = Point(0, 0)
mf_cursor_pos = Point(0, 0)
cf_cursor_pos = Point(0, 0)
new_track_y = 0
new_data_y = 0
mode = 0
command = ""

main_frame = Box(0, 0, 0, 0)
command_frame = Box(0, 0 ,0, 0)
current_frame = None

printed_tracks = []
printed_metadata = []

highlighted_t = []
highlighted_md = []

manager_method = None
args = ()
kwargs = {"picked_tracks": highlighted_t, "picked_metadata": highlighted_md}

def read_key():
    key = msvcrt.getwch()
    if ord(key) == 0:
        key = msvcrt.getwch()
    return ord(key)

def clear_char():
    cursor_left()
    print("\033[1P", end="", flush=True)

def clear_line_backward():
    print("\033[1K", end="", flush=True)

def clear_line_forward():
    print("\033[0K", end="", flush=True)

def clear_command():
    if len(command) == 0:
        return
    move_cursor(Point(command_frame.left, command_frame.top))
    clear_line_forward()

def clear_screen():
    print("\033[2J", end="", flush=True)

def clear_screen_forward():
    print("\033[0J", end="", flush=True)

def set_color(c):
    print(c, end="", flush=True)

def move_cursor(destination):
    h = "\033[{0}G".format(destination.x)
    v = "\033[{0}d".format(destination.y)

    print(h + v, end="", flush=True)

    global cursor_pos
    cursor_pos = destination

def cursor_up():
    if cursor_pos.y <= current_frame.top:
        return
    
    print(ESC_CHARS["up"], end="", flush=True)
    cursor_pos.y -= 1

def cursor_right():
    if cursor_pos.x >= current_frame.right:
        return
    
    print(ESC_CHARS["right"], end="", flush=True)
    cursor_pos.x += 1

def cursor_down():
    if cursor_pos.y >= current_frame.bottom:
        return
    
    print(ESC_CHARS["down"], end="", flush=True)
    cursor_pos.y += 1

def cursor_left():
    if cursor_pos.x <= current_frame.left:
        return
    
    print(ESC_CHARS["left"], end="", flush=True)
    cursor_pos.x -= 1

def highlight_track(index):
    old_cursor_pos = cursor_pos
    move_cursor(Point(1, index + main_frame.top + 1))
    
    color = PALLETE["blue_color"]
    if highlighted_t[index]:
        color = PALLETE["no_color"]
    
    set_color(color)
    put_track_line(str(index + 1), printed_tracks[index])
    set_color(PALLETE["no_color"])

    highlighted_t[index] = not highlighted_t[index]
    move_cursor(old_cursor_pos)

def highlight_metadata_item(index):
    old_cursor_pos = cursor_pos
    move_cursor(Point(WIDTH // 2 + 1, index + main_frame.top + 1))
    
    color = PALLETE["red_color"]
    if highlighted_md[index]:
        color = PALLETE["no_color"]
    
    set_color(color)
    put_metadata_line(*printed_metadata[index])
    set_color(PALLETE["no_color"])

    highlighted_md[index] = not highlighted_md[index]
    move_cursor(old_cursor_pos)

def highlight():
    if cursor_pos.x <= WIDTH // 2:
        idx = cursor_pos.y - main_frame.top - 1
        if not (0 <= idx < len(printed_tracks)):
            return
        highlight_track(idx)
        return
    
    if WIDTH // 2 < cursor_pos.x <= WIDTH:
        idx = cursor_pos.y - main_frame.top - 1
        if not (0 <= idx < len(printed_metadata)):
            return
        highlight_metadata_item(idx)
        return
    
def highlight_all_tracks(p: bool):
    for i in range(len(printed_tracks)):
        if highlighted_t[i] != p:
            highlight_track(i)
    
def highlight_all_metadata(p: bool):
    for i in range(len(printed_metadata)):
        if highlighted_md[i] != p:
            highlight_metadata_item(i)
    
def highlight_all(p: bool):
    if cursor_pos.x <= WIDTH // 2:
        highlight_all_tracks(p)
        return
    
    if WIDTH // 2 < cursor_pos.x <= WIDTH:
        highlight_all_metadata(p)
        return

def put_char(ch):
    print("\033[4h", end="", flush=True)
    msvcrt.putwch(ch)
    print("\033[4l", end="", flush=True)
    cursor_pos.x += 1

def put_line(l):
    new_line = False
    if l[-1] == '\n':
        new_line = True

    if new_line:
        print(l[:-1], end="", flush=True)
        move_cursor(Point(1, cursor_pos.y + 1))
        return
    
    print(l, end="", flush=True)
    move_cursor(Point(cursor_pos.x + len(l), cursor_pos.y))

def put_track_line(i, track):
    if len(i + track) + 2 >= WIDTH // 2:
        track = track[:WIDTH // 2 - len(i + track) - 6] + "..."

    track_line = "{0}. {1}".format(i, track)
    put_line(track_line)

def put_metadata_line(key, value):
    if len(key) >= 28:
        key = key[:25] + "..."
    
    if len(value) >= 29:
        value = value[:26] + "..."

    line = "{0}: {1}".format(key, value)
    put_line(line)

def add_tracks(tracks):
    global new_track_y, current_frame, main_frame, command_frame, cursor_pos

    old_cursor_pos = mf_cursor_pos if current_frame == main_frame else cf_cursor_pos
    
    overflow = False
    i = len(printed_tracks)
    for track in tracks:
        if new_track_y >= main_frame.bottom:
            overflow = True
            move_cursor(Point(1, new_track_y))
            clear_screen_forward() # maybe optimize
            move_cursor(Point(WIDTH // 2, new_track_y))
            put_line("|")
            move_cursor(Point(WIDTH, new_track_y))
            put_line("|")
        
        move_cursor(Point(1, new_track_y))
        put_track_line(str(i + 1), track)

        new_track_y += 1
        i += 1

        printed_tracks.append(track)
        highlighted_t.append(False)
    
    if overflow:
        move_cursor(Point(1, new_track_y))
        put_line("-" * WIDTH + "\n")
        put_line("init> ")

        main_frame.bottom = new_track_y
        command_frame.top = new_track_y + 1
        command_frame.bottom = command_frame.top

    move_cursor(Point(current_frame.left, current_frame.top) + old_cursor_pos)

def add_metadata(metadata):
    global new_data_y, current_frame, main_frame, command_frame, cursor_pos

    old_cursor_pos = mf_cursor_pos if current_frame == main_frame else cf_cursor_pos
    
    overflow = False
    for key, value in metadata:
        if new_data_y >= main_frame.bottom:
            overflow = True
            move_cursor(Point(1, new_data_y))
            clear_screen_forward() # maybe optimize
            move_cursor(Point(WIDTH // 2, new_data_y))
            put_line("|")
            move_cursor(Point(WIDTH, new_data_y))
            put_line("|")

        move_cursor(Point(WIDTH // 2 + 1, new_data_y))
        put_metadata_line(key, value)

        new_data_y += 1

        printed_metadata.append((key, value))
        highlighted_md.append(False)
    
    if overflow:
        move_cursor(Point(1, new_data_y))
        put_line("-" * WIDTH + "\n")
        put_line("init> ")

        main_frame.bottom = new_data_y
        command_frame.top = new_data_y + 1
        command_frame.bottom = command_frame.top
    
    move_cursor(Point(current_frame.left, current_frame.top) + old_cursor_pos)

def remove_tracks(tracks_to_remove):
    global new_track_y
    global cursor_pos
    global main_frame

    i = tracks_to_remove[0]

    for index in reversed(tracks_to_remove):
        printed_tracks.pop(index)

    old_cursor_pos = cursor_pos

    while i < len(printed_tracks):  
        move_cursor(Point(WIDTH // 2 - 1, main_frame.top + i + 1))
        clear_line_backward()
        move_cursor(Point(1, main_frame.top + i + 1))
        put_track_line(str(i + 1), printed_tracks[i])
        i += 1
        move_cursor(Point(1, main_frame.top + i + 1))

    buf = cursor_pos.y

    while cursor_pos.y < new_track_y:
        move_cursor(Point(WIDTH // 2 - 1, cursor_pos.y))
        clear_line_backward()
        cursor_pos.y += 1
    
    if new_track_y > new_data_y:
        main_frame.bottom = max(new_data_y, buf)

        move_cursor(Point(1, main_frame.bottom))
        clear_screen_forward()
        put_line("-" * WIDTH + "\n")
        put_line("init> ")

    new_track_y = buf

    old_cursor_pos.y = min(old_cursor_pos.y, command_frame.bottom)
    move_cursor(old_cursor_pos)

def remove_metadata(data_to_remove):
    global new_data_y
    global cursor_pos
    global main_frame

    i = data_to_remove[0]

    for index in reversed(data_to_remove):
        printed_metadata.pop(index)

    old_cursor_pos = cursor_pos
    move_cursor(Point(WIDTH // 2 + 1, main_frame.top + 1))

    while i < len(printed_metadata):
        move_cursor(Point(WIDTH // 2 + 1, main_frame.top + i + 1))
        clear_line_forward()
        put_metadata_line(*printed_metadata[i])
        move_cursor(Point(WIDTH, cursor_pos.y))
        put_line("|")

        i += 1
        move_cursor(Point(1, main_frame.top + i + 1))

    buf = cursor_pos.y

    while cursor_pos.y < new_data_y:
        move_cursor(Point(WIDTH // 2 + 1, cursor_pos.y))
        clear_line_forward()
        move_cursor(Point(WIDTH, cursor_pos.y))
        put_line("|")
        cursor_pos.y += 1
    
    if new_track_y < new_data_y:
        main_frame.bottom = max(new_track_y, buf)

        move_cursor(Point(1, main_frame.bottom))
        clear_screen_forward()
        put_line("-" * WIDTH + "\n")
        put_line("init> ")

    new_data_y = buf

    old_cursor_pos.y = min(old_cursor_pos.y, command_frame.top)
    move_cursor(old_cursor_pos)

def switch_mode():
    global mode
    global current_frame
    global mf_cursor_pos
    global cf_cursor_pos

    if mode == NAVIGATION_MODE:
        mf_cursor_pos = cursor_pos - Point(current_frame.left, current_frame.top)
        
        current_frame = command_frame
        mode = COMMAND_MODE

        new_cursor_pos = Point(current_frame.left, current_frame.top) + cf_cursor_pos
        move_cursor(new_cursor_pos)
    else:
        cf_cursor_pos = cursor_pos - Point(current_frame.left, current_frame.top)

        current_frame = main_frame
        mode = NAVIGATION_MODE

        new_cursor_pos = Point(current_frame.left, current_frame.top) + mf_cursor_pos
        move_cursor(new_cursor_pos)

def change_printed(old_list, new_list):
    index = 0
    diff_pos = 0

    while (index < len(old_list)) or (index < len(new_list)):
        if index >= len(old_list):
            yield Point(1, cursor_pos.y)
            index += 1
            continue
        
        diff_pos = compare_strings(old_list[index], new_list[index])
        if diff_pos == len(new_list[index]):
            index += 1
            continue
        yield Point(diff_pos, cursor_pos.y)
        index += 1

def create_layout():
    global new_track_y, new_data_y, main_frame, command_frame, current_frame, mf_cursor_pos, cf_cursor_pos, mode, current_scope
    
    clear_screen()
    move_cursor(Point(1, 1))
    put_line("TRACKS")
    move_cursor(Point(WIDTH // 2, 1))
    put_line("|METADATA")
    move_cursor(Point(WIDTH, 1))
    put_line("|\n")
    put_line("-" * WIDTH + "\n")
    put_line("-" * WIDTH + "\n")
    put_line("init> ")

    new_track_y = 3
    new_data_y = 3

    main_frame = Box(2, WIDTH, 3, 1)
    command_frame = Box(4, WIDTH, 4, 7)

    mf_cursor_pos = Point(WIDTH//2 - 1, 0)

    current_frame = command_frame

    mode = COMMAND_MODE

def refresh():
    global command, highlighted_t, highlighted_md

    if len(command) != 0:
        clear_command()

    highlight_all_tracks(False)
    highlight_all_metadata(False)

def process_key(key):
    global command, manager_method, args, kwargs

    processed = False

    match key:
        case 3: # ctrl + c
            switch_mode()
            processed = True
        case 72: # up
            cursor_up()
            processed = True
        case 77: # right
            cursor_right()
            processed = True
        case 80: # down
            cursor_down()
            processed = True
        case 75: # left
            cursor_left()
            processed = True
    
    if processed:
        return 0

    commit = False

    if mode == NAVIGATION_MODE:
        match key:
            case 111: # o
                manager_method = manager.get_metadata
            case 115: # s
                highlight()
            case 1: # ctrl + a
                highlight_all(True)
            case 113: # q
                manager_method = manager.quit
                args = ()
            case 13: # enter
                command = ""
                commit = True

    elif mode == COMMAND_MODE:
        p = cursor_pos.x - command_frame.left
        if chr(key).isprintable():
            put_char(chr(key))
            command = command[:p] + chr(key) + command[p:]
        elif key == 8: # backspace
            clear_char()
            command = command[:p-1] + command[p:]
        elif key == 13: # enter
            manager_method, *args = ci.execute_command(command)
            command = ""
            commit = True

    if commit:
        ui_changes = manager_method(*args, **kwargs)
        refresh()
        return apply_changes(ui_changes)
        
    return 0

def apply_changes(ui_changes):
    match ui_changes:
        case AddTracks():
            add_tracks(ui_changes.content)
        case RemoveTracks():
            remove_tracks(ui_changes.content)
        case AddMetadata():
            if len(printed_metadata) != 0:
                remove_metadata([i for i in range(len(printed_metadata))]) # kill me
            add_metadata(ui_changes.content)
        case QuitApp():
            clear_screen()
            move_cursor(Point(1, 1))
            # restore console history somehow
            return 1
    
    return 0

if __name__ == "__main__":
    key = msvcrt.getwch()
    if ord(key) == 0:
        print("haha")
        key = msvcrt.getwch()
    print(ord(key))
