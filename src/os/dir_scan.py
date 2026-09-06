from pathlib import Path
import sys
import re
from colors import RED, DEFAULT, PURPLE, GREEN, YELLOW

if sys.platform == "win32":
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

counter = 0
rawpath = ""
params = []
scanmode = 0
path = ""

def recv_data(): 
    """
        Recebe os dados de entrada (caminho, modo de varredura e termos)
    """

    global rawpath
    global params
    global scanmode
    global path

    rawpath = input('Insira o caminho da pasta: ')

    scanmode_nready = True

    while scanmode_nready:
        scanmode = int(input('Modo de varredura:\n\n0 - Qualquer arquivo com o nome ou a extensão\n1 - Arquivo com o nome e a extensão juntos\n2 - Todos os arquivos\n'))

        if scanmode == 0:
            params = input(f'Insira os termos e as extensões\n\nExemplo: termo1, termo2:.csv, .txt\n\n{RED}Use "*" quando o nome ou a extensão não importarem: {DEFAULT}').split(":")
            scanmode_nready = False
            params = [ params[0].split(","), params[1].split(",") ]
        elif scanmode == 1:
            params = input(f'Insira {RED}obrigatóriamente{DEFAULT} os termos e as extensões\n\nExemplo: termo1, termo2:.csv, .txt\n\n').split(":")
            scanmode_nready = False
            params = [ params[0].split(","), params[1].split(",") ]
        elif scanmode == 2:
            scanmode_nready = False
        else:
            print("Insira um modo de varredura válido.\n")
        
    path = Path(rawpath.strip())

def term_in_name(term, name):
    """
        Verifica se o termo existe no nome do arquivo via regex.

        Args:   
            term (string): termo que será buscado
            name (string): nome do arquivo
    """

    secure_term = re.escape(term)
    return re.search(secure_term, name, re.IGNORECASE)

def print_finded(filename, path):
    """
        Printa o arquivo encontrado com o caminho.

        Args:   
            filename (string): nome do arquivo
            path (Path): caminho do arquivo
    """
    
    print(f'{GREEN}[{filename}]{DEFAULT} encontrado em {PURPLE}{path}{DEFAULT}')

def r_search_gen(path : Path):
    """
        Realiza uma busca recursiva para encontrar todos os arquivos com os nomes OU as extensões indicadas.

        Args:   
            path (Path): caminho do sub-diretório
    """
    
    global counter

    for entity in path.iterdir():
        if not entity.is_file():
            r_search_gen(path / entity.name)
        else:
            filename = entity.stem
            ext = entity.suffix

            for term in params[0]:
                if(term == "*"): pass

                if(term_in_name(term.strip(), filename)): 
                    counter += 1
                    print_finded(entity.name, path / entity.name)

            for especific_ext in params[1]:
                if(especific_ext == "*"): pass

                if(especific_ext == ext): 
                    counter += 1
                    print_finded(entity.name, path / entity.name)

def r_search_especific(path : Path):
    """
        Realiza uma busca recursiva para encontrar todos os arquivos com os nomes E as extensões indicadas.

        Args:   
            path (Path): caminho do sub-diretório
    """
    
    global counter

    for entity in path.iterdir():
        if not entity.is_file():
            r_search_especific(path / entity.name)
        else:
            filename = entity.stem
            ext = entity.suffix

            has_correct_name = False

            for term in params[0]:
                if(term_in_name(term.strip(), filename)): 
                    has_correct_name = True
                    break

            for especific_ext in params[1]:
                if(especific_ext == ext and has_correct_name): 
                    counter += 1
                    print_finded(entity.name, path / entity.name)

def r_search_all(path : Path):
    """
        Realiza uma busca recursiva para encontrar todos os arquivos.

        Args:   
            path (Path): caminho do sub-diretório
    """

    global counter

    for entity in path.iterdir():
        if not entity.is_file():
            r_search_all(path / entity.name)
        else:
            counter += 1
            print_finded(entity.name, path / entity.name)

running = True
modes = [
    r_search_gen,
    r_search_especific,
    r_search_all
]

while(running):
    counter = 0
    recv_data()

    if path.exists():
        mode = modes[scanmode]
        mode(path)

        print(f'\n{YELLOW}{counter} arquivos encontrados.{DEFAULT}')
    else:
        print("\nO caminho informado não existe ou esta escrito incorretamente.")

    retry = input("\nDeseja realizar mais uma varredura? s/n: ").strip()

    if(retry == "s"): continue
    else:             running = False

input("\nPressione ENTER para sair")
