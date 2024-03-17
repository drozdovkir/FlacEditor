def parse_command(command):
    command = command.strip()
    command += ' '
    
    state = "initial"
    lexems = []
    current_lexem = ""

    for ch in command:
        # print(ch)
        # print(state)
        # print()
        match state:
            case "initial":
                if ch == ' ':
                    continue
                if ch.isupper():
                    current_lexem += ch
                    state = "keyword"
                elif ch.isalpha():
                    current_lexem += ch
                    state = "command"
                elif (ch == '[') or (ch == ',') or (ch == ':'):
                    lexems.append(ch)
                elif ch == '"':
                    current_lexem += ch
                    state = "name"
                elif ch.isdigit():
                    current_lexem += ch
                    state = "index"
                elif ch == ']':
                    lexems.append(ch)
                    state = "]"
                else:
                    state = "error"

            case "command":
                if ch.isalpha():
                    current_lexem += ch
                elif ch == ' ':
                    lexems.append(current_lexem)
                    current_lexem = ""
                    state = "initial"
                else:
                    state = "error"

            case "name":
                if ch == '"':
                    current_lexem += ch
                    lexems.append(current_lexem)
                    current_lexem = ""
                    state = "initial"
                else:
                    current_lexem += ch

            case "index":
                if ch.isdigit():
                    current_lexem += ch
                elif ch == ' ':
                    lexems.append(current_lexem)
                    current_lexem = ""
                    state = "initial"
                elif (ch == ']') or (ch == ','):
                    lexems.append(current_lexem)
                    current_lexem = ""
                    lexems.append(ch)
                    state = "initial"
                else:
                    state = "error"
            
            case "keyword": # keyword in vorbis comments section
                if ch.isupper():
                    current_lexem += ch
                elif ch == ' ':
                    lexems.append(current_lexem)
                    current_lexem = ""
                    state = "initial"
                elif ch == ':':
                    lexems.append(current_lexem)
                    current_lexem = ""
                    lexems.append(ch)
                    state = "initial"
                else:
                    state = "error"

            case "]": # ensure that there is always space after ]
                if ch == ' ':
                    state = "initial"
                else:
                    state = "error"

            case "error":
                return None
    
    if state != "initial":
        return None

    return lexems


class CommandInterface():
    def __init__(self, manager):
        self.scope = 0
        self.manager = manager

    def execute_command(self, command):
        lexems = parse_command(command)
        if lexems is None:
            return None

        try:
            func, arg = self._parse_lexems(lexems)
        except SyntaxError as e:
            pass

        return func, arg

    def _parse_lexems(self, lexems):
        if lexems[0] == "import":
            p = lexems[1].strip('"')
            return self.manager.import_tracks, ([p,])
        
        if lexems[0] == "quit":
            return self.manager.quit, None
    


def parse_lexems(lexems):

    scope = "initial"
    inside_list = False
    execute = False

    songs = []
    data = {}

    for lexem in lexems:
        match scope:
            case "initial":
                if (lexem == "s") or (lexem == "songs"):
                    scope = "songs"
                elif (lexem == "d") or (lexem == "data"):
                    scope = "data"
                elif lexem == "add":
                    scope = "adding"
                elif lexem == "set":
                    execute = True
                else:
                    state = "error"
                
            case "songs":
                if lexem == "[":
                    state = "song_list"
                elif (lexem.startswith('"')) or (lexem.isdigit()):
                    songs.append(lexem)
                    state = "initial"
                elif (lexem == "d") or (lexem == "data"):
                    state = "data"
                else:
                    state = "error"

            case "data":
                if lexem.isupper():
                    data[lexem] = None
                    state = "keyword_read"
                elif lexem == "[":
                    state = "data_list"
                else:
                    state = "error"   

if __name__ == "__main__":
    command = input()
    lexems = parse_command(command)
    if lexems is None:
        print("error")
    else:
        for lexem in lexems:
            print(lexem)
