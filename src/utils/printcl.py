from utils.colors import ansicolors

colors = ansicolors()

def printcl(color, text):
    print(f'{colors[color]}{text}{colors['DEFAULT']}')

def printcl_concat(*words: tuple[str, str]):
    colored_str = ""

    for word in words:
        colored_str += f'{colors[word[0]]}{word[1]}{colors['DEFAULT']}'  

    print(colored_str)  