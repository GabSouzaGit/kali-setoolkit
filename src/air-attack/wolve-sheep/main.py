"""
Tasks:

    - Deixar usuário definir interface no menu da aplicação

"""

# WVS = WolVeSheep

import os
import subprocess
import sys
import ctypes 
import platform  
import random
import shutil
import threading
import re

# Erros e riscos
WVS_ERRORS = [
    "Ação desconhecida. Insira um dos comandos do menu.",
    "Falha ao iniciar DHCP (dnsmasq). Verifique o arquivo de configuração em config/ap_dhcp.conf",
    "Falha ao abrir ponto de acesso (hostapd). Verifique o arquivo de configuração em config/hostapd.conf",
    "A interface informada não tem suporte para ponto de acesso.",
    "Interface não identificada ou desconectada. Verifique a conexão do dispositivo e tente novamente.",
    "Elimine o processo da porta e tente novamente.",
    "Falha ao iniciar serviço DHCP. Verifique o status do dnsmasq em sua máquina."
]

WVSERR_UNKNOWN_ACTION           = 0
WVSERR_DHCP_START               = 1
WVSERR_HOSTAPD_START            = 2
WVSERR_AP_NOT_SUPPORTED         = 3
WVSERR_INTERFACE_NOT_FOUND      = 4
WVSERR_PORT_CONFLICT            = 5
WVSERR_DNSMASQ_START_FAILURE    = 6

# Portas e serviços
DHCP_PORT            = 53
NETWORK_INTERFACE_IP = "192.168.50.1/24"

DEPENDENCIES = [
    "hostapd",
    "airmon-ng",
    "airodump-ng",
    "python3",
    "dnsmasq"
]

# Suporte e verificação
SUPPORT_MODES_TITLE          = "Supported interface modes:"
NETWORK_INTERFACE_AP_SUPPORT = "* AP"

# Prefixos e opções de console
CSTOPIC_PREFIX     = "[+]"
CSWARN_PREFIX      = "[-]"
CSINPUT_PREFIX     = "[?]"
CSCRITICAL_PREFIX  = "[!]"
WOLVESHEEP_WAITING = "wolvesheep"
TABLE_WIDTH        = 100

# Caminhos padrão da aplicação
HOSTAPD_PATHNAME   = "config/hostapd.conf"
DNSMASQ_PATHNAME   = "config/ap_dhcp.conf"
SETUP_BANNER_FILE  = "setup-banner.txt"

# Ações do menu
WVS_AP_CREATION_ACTION = "/ap"
WVS_AIRSCAN_ACTION     = "/airscan"
WVS_SERVICES_ACTION    = "/services"
WVS_ATTACKS_ACTION     = "/attacks"
WVS_EXITLOOP_ACTION    = "exit"

# Configurações do ponto de acesso
AP_CHANNEL                   = 6
AP_INTERFACE                 = "wlan0"
AP_DRIVER                    = "nl80211"
AP_HW_MODE                   = "g"
AP_CCD                       = "BR"
AP_PIEE80211N                = "1"
AP_WMM_ENABLED               = "1"
AP_AUTH_ALGS                 = "1"
AP_MACADDR_ACL               = "0"
AP_BROADCAST_SSIDIGNORE      = "0"

AP_ESSID                     = "Rede publica"
AP_PHISHING_SERVICE          = "0"

ANSICOLORS = {
    "red":      '\033[0;38;2;255;56;56;49m',
    "green":    '\033[0;38;2;17;255;0;49m',
    "blue":     '\033[0;38;2;82;125;255;49m',
    "yellow":   '\033[0;93;49m',
    "orange":   '\033[0;38;2;255;149;0;49m',
    "cyan":     '\033[0;96;49m',
    "default":  '\033[0;39;49m'
}

class WVSException(Exception):
    def __init__(self, id : int):
        super().__init__(WVS_ERRORS[id])

# Informações de sistema, configurações iniciais, compatibilidade e verificações
closure_due_to_incompatibility = False

def os_dump():
    return {
        "arch":     platform.architecture(),
        "platform": sys.platform,
        "sys":      platform.system(),
        "osname":   os.name,
        "release":  platform.release(),
        "machine":  platform.machine()
    }

def attr_interface_ip(interface : str):
    interface_ip = subprocess.run(
        "ip -4 -o addr show "+interface+" | awk '{print $4}'",
        shell=True,
        capture_output=True,
        text=True
    ).stdout

    if interface_ip == "":
        subprocess.run(
            f"sudo ip addr add {NETWORK_INTERFACE_IP} dev {interface}",
            shell=True
        )

        print_as_topic(f"IP {cstr("green", NETWORK_INTERFACE_IP)} atribuido à interface {cstr("green", interface)}.")


def network_interface_ready(interface : str):
    ip_interfaces = subprocess.run(
        "ip -br link",
        capture_output=True,
        text=True,
        shell=True
    )

    interface_exists = False

    for line in ip_interfaces.stdout.splitlines():
        sys_interface = line.split()[0]

        if sys_interface == interface:
            interface_exists = True

    if interface_exists:
        phy_details = subprocess.run(
            "iw list",
            capture_output=True,
            text=True,
            shell=True
        )

        check_support = False

        for line in phy_details.stdout.splitlines():
            line = line.strip()

            if line == SUPPORT_MODES_TITLE:
                check_support = True
                continue

            if check_support:
                if line.startswith("*"):
                    if line == NETWORK_INTERFACE_AP_SUPPORT:
                        attr_interface_ip(interface)
                        return True
                else:
                    raise WVSException(WVSERR_AP_NOT_SUPPORTED)
    
    raise WVSException(WVSERR_INTERFACE_NOT_FOUND)

SYS_INFO = os_dump()

# Gerenciamento de processos
def test_process(pname : str):
    pdef = shutil.which(pname)
    return pdef

def process_failed(process : subprocess.Popen):
    return process.poll() is not None
    
def os_warnings():
    warnings = []
    missing_dependencies = []

    if(SYS_INFO["sys"] != "Linux" and  SYS_INFO["sys"] != "FreeBSD"):
        warnings.insert(0, ["Esta release atual é funcional apenas em ambiente Linux ou FreeBSD.", 1])
        global closure_due_to_incompatibility

        closure_due_to_incompatibility = True
    else:
        distro_info = platform.freedesktop_os_release().get("ID")

        if(distro_info != "kali"):
            warnings.append(["Apesar do uso em ambiente Linux, recomendamos a distro Kali para melhores resultados. ", 0])

        for lib in DEPENDENCIES:
            lib_exists = test_process(lib)

            if(not lib_exists):
                missing_dependencies.append([lib, 0])

    return {
        "warnings": warnings,
        "missing-dependencies": missing_dependencies
    }

def compatibility_dump():
    global closure_due_to_incompatibility

    dump = os_warnings()

    warn_level = [
        warn,
        critical
    ]

    if(len(dump["warnings"]) > 0):
        printc("red", "AVISOS IMPORTANTES: \n")
        for warning in dump["warnings"]:
            [warn_text, level] = warning
            warn_level[level](warn_text)

        print("\n")

    if(len(dump["missing-dependencies"]) > 0):
        closure_due_to_incompatibility = True

        printc("red", "DEPENDENCIAS AUSENTES: \n")

        for dependencie in dump["missing-dependencies"]:
            [dependencie_name, level] = dependencie

            warn_level[level](dependencie_name)

        print("~ Certifique-se de baixar os pacotes necessários para a execução adequada do programa.")
            
    if(closure_due_to_incompatibility): 
        exit()

# ISSUES
#   * Adaptar logtypes

# Network e ponto de acesso
def realtime_tracking(hostapd : subprocess.Popen, interface : str):
    def handle_another_logtype(splitted : list[str], line : str):
        logtype = splitted[0].removesuffix(":")

        HANDLE_PROBE_REQ = logtype == "handle_probe_req"
        HANDLE_ASSOC_CB  = logtype == "handle_assoc_cb"

        if HANDLE_PROBE_REQ:
            print("Entrou no Probe Request")
            print(splitted)
            if splitted[1] == "send failed":
                return "Falha ao enviar frame de requisição."
            else:
                return line

        if HANDLE_ASSOC_CB:
            rgx_not_found = r'not found'

            CB_NOT_FOUND = re.search(rgx_not_found, line)

            if CB_NOT_FOUND:
                mac_device = cstr("green", splitted[2])
                return f"Dispositivo {mac_device} não foi encontrado durante a associação."

            return line

        return line

    def handle_sta_interaction(splitted : list[str], line : str):
        interation = splitted[1]
        mac_device = cstr("green", splitted[2])

        STA                 = interation == "STA"
        AP_STA_CONNECTED    = interation == "AP-STA-CONNECTED"
        AP_STA_DISCONNECTED = interation == "AP-STA-DISCONNECTED"

        if STA:
            rgx_iee_association    = r'IEEE 802.11: associated'
            rgx_accounting_session = r'RADIUS: starting accounting session'

            IS_IEEE_ASSOC         = re.search(rgx_iee_association, line)
            IS_ACCOUNTING_SESSION = re.search(rgx_accounting_session, line)

            if IS_IEEE_ASSOC:
                return f"Dispositivo {mac_device} se associou com ponto de acesso {splitted[len(splitted) - 1]}"

            elif IS_ACCOUNTING_SESSION:
                return f"Dispositivo {mac_device} iniciou sessão de conta via RADIUS."
            else:
                return f"Dispositivo {mac_device} interagiu com o ponto de acesso."

        if AP_STA_CONNECTED:
            return f"Dispositivo {mac_device} se conectou ao ponto de acesso."
        
        if AP_STA_DISCONNECTED:
            return f"Dispositivo {mac_device} se desconectou do ponto de acesso."

    def update_table(line : str):
        rgx_interface_state = r'interface state'

        logtype = {
            "handle_probe_req:": True,
            "handle_assoc_cb:":  True
        }

        ap_status = {
            "AP-ENABLED": cstr("green", "Ponto de acesso on-line."),
            "AP-DISABLED": cstr("red", "Ponto de acesso off-line."),
            "INTERFACE-DISABLED": cstr("red", "Interface off-line."),
            "INTERFACE-ENABLED": cstr("green", "Interface on-line."),
        }

        interface_states = {
            "UNINITIALIZED->COUNTRY_UPDATE": "Atualizando configurações regulatórias do país...",
            "COUNTRY_UPDATE->ENABLED": "Interface habilitada.",
        }

        stations = {
            "STA": True,
            "AP-STA-CONNECTED": True,
            "AP-STA-DISCONNECTED": True
        }

        status = cstr("green", "[WOLVESHEEP]: ")
        splitted = line.split()

        # Condições iniciais
        IS_NOT_INTERFACE_LOG  = splitted[0].removesuffix(":") != interface
        IS_AP_STATUS          = splitted[1] in ap_status
        IS_INTERFACE_STATE    = re.search(rgx_interface_state, line)
        IS_STA_INTERACTION    = splitted[1] in stations

        if IS_NOT_INTERFACE_LOG:
            status += handle_another_logtype(splitted, line)

        elif IS_AP_STATUS:
            status += ap_status[splitted[1]]

        elif IS_STA_INTERACTION:
            status += handle_sta_interaction(splitted, line)
        
        elif IS_INTERFACE_STATE:
            state = splitted[len(splitted) - 1]

            if state in interface_states:
                status += interface_states[state]
            else:
                status += cstr("yellow", "Estado da interface desconhecido.")


        table_line(status)

    table_start() # INICIO DA TABELA
    table_structure()

    try:
        for line in hostapd.stdout:
            update_table(line) # ALIMENTAÇÃO DA TABELA
    except KeyboardInterrupt:
        table_line(f'{cstr("green", "[WOLVESHEEP]: ")} encerrando programa...')
    finally:
        hostapd.terminate()
        hostapd.wait()

        subprocess.run(
            "sudo systemctl stop dnsmasq",
            shell=True
        )

def open_ap_listening(interface : str):
    print("\n")

    hostapd = subprocess.Popen(
        ["sudo", "hostapd", HOSTAPD_PATHNAME],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    if process_failed(hostapd):
        raise WVSException(WVSERR_HOSTAPD_START)

    print("\n")

    realtime_tracking(hostapd, interface)

def hostapd_config_init(
            ap_interface : str,
            ap_channel : str,
            ap_driver : str,
            ap_essid : str,
            ap_phishing_service : str):
    with open(HOSTAPD_PATHNAME, "w") as file:
        hostapd_conf = {
            "interface":             ap_interface,
            "driver":                ap_driver,
            "ssid":                  ap_essid,
            "country_code":          AP_CCD,
            "hw_mode":               AP_HW_MODE,
            "channel":               ap_channel,
            "ieee80211n":            AP_PIEE80211N,
            "wmm_enabled":           AP_WMM_ENABLED,
            "auth_algs":             AP_AUTH_ALGS,
            "macaddr_acl":           AP_MACADDR_ACL,
            "ignore_broadcast_ssid": AP_BROADCAST_SSIDIGNORE
        }

        for key, value in hostapd_conf.items():
            file.write(f"{key}={value}\n")

        cclear()

# ISSUE
# * Verificar falha de abertura de serviço (ocupação de porta 53 e LOOPBACK_IP) 
def inspect_port(port : int):
    ss_look = subprocess.run(
        "sudo ss -tulpn sport = :"+str(port)+" | awk 'NR == 1 {print $1, $5, $7; next} {print $1, $5, $7}'",
        capture_output=True,
        text=True,
        shell=True
    )

    if ss_look.returncode != 0: return None

    inspection = {
        "free": True,
        "services": []
    }

    processes = ss_look.stdout.strip().splitlines()
    rgx_extract_pname = r'".+"' # Captura o processo (("dnsmasq", ...))

    if len(processes) <= 1: return inspection

    inspection["free"] = False

    for process in processes[1:]:
        process = process.split()

        last_index   = len(process) - 1
        process_name = re.search(rgx_extract_pname, process[last_index]).group().strip('"')

        if process_name in inspection["services"]:
            continue

        inspection["services"].append(process_name)

    return inspection

def kill_processes(processes : list[str]):
    for process in processes:
        killed = subprocess.run(
            f"sudo pkill -SIGKILL {process}",
            capture_output=True,
            text=True,
            shell=True
        )

        if killed.returncode != 0:
            continue

        processes.remove(process)

    return processes

def dhcp_start():
    processes = inspect_port(DHCP_PORT)

    if processes == None:
        warn("Não foi possível verificar a porta DHCP (53). Caso a porta esteja ocupada por outro serviço, ele não funcionará.")
    elif processes["free"] != True:
        pendent_processes = kill_processes(processes["services"])

        if pendent_processes:
            critical("Há serviços ainda conflitando com a porta DHCP (53):")

            for process in pendent_processes:
                print(f"    * {process}")

            print("\n")
            raise WVSException(WVSERR_PORT_CONFLICT)

    dnsmasq = subprocess.Popen(
        ["sudo", "dnsmasq", "--no-daemon", "-C", f"{DNSMASQ_PATHNAME}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    if dnsmasq.poll() is None: 
        print_as_topic(f"DHCP online.")
    else:
        raise WVSException(WVSERR_DNSMASQ_START_FAILURE)

def dnsmasq_config_init(interface : str):
    with open(DNSMASQ_PATHNAME, "w") as file:
        dnsmasq_conf = {
            "interface": interface,
            "bind-dynamic": "",
            "dhcp-range": "192.168.50.20,192.168.50.100,255.255.255.0,12h",
            "dhcp-option": [
                "option:router,192.168.50.1",
                "option:dns-server,192.168.50.1"
            ]
        }

        for key, value in dnsmasq_conf.items():
            if value == "":
                file.write(f"{key}\n")
                continue

            if isinstance(value, list):
                for subvalue in value:
                    file.write(f"{key}={subvalue}\n")
                
                continue

            file.write(f"{key}={value}\n")

def kill_network_processes():
    check = subprocess.run("sudo airmon-ng check kill", shell=True)

# Configurações de cor ANSI e I/O
def load_ascii_art(filename : str, color : str = "default"):
    with open(f'ascii-arts/{filename}', 'r') as file:
        for line in file:
            printc(color, line, end='')

    print("\n")

def wincli_accept_ansicolor():
    if(SYS_INFO["platform"] == "win32"):
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def underline_string(text : str):
        return f'\033[1;4;39;49m{text}\033[0m'

def cstr(color : str, text : str):
    return f'{ANSICOLORS[color]}{text}{ANSICOLORS['default']}'

def printc(color : str, text : str, end='\n'):
    print(f'{cstr(color, text)}', end=end)

def wvs_input(text : str):
    return input(f'{cstr('cyan', CSINPUT_PREFIX)} {text}: ')

def create_interface_command():
    default = lambda df_value: f"Pressione ENTER para usar o padrão (default '{cstr("green", df_value)}')"

    def ap():
        def ap_config_dump(
            interface : str,
            channel : str,
            driver : str,
            essid : str,
            service : str
        ):
            load_ascii_art(SETUP_BANNER_FILE)
            print("\n")

            print(40 * '-')
            print(f'{cstr("green", "INTERFACE")}: {cstr("orange", interface)}')
            print(f'{cstr("green", "CANAL")}: {cstr("orange", channel)}')
            print(f'{cstr("green", "DRIVER")}: {cstr("orange", driver)}')
            print(f'{cstr("green", "ESSID")}: {cstr("orange", essid)}')
            print(f'{cstr("green", "SERVIÇO DE PHISHING")}: {cstr("orange", "OPERADORA VIVO 2026")}')
            print(40 * '-')

            print("\n")

            return input(f'Deseja prosseguir com a configuração? {cstr("cyan", "[Y,n]")}').lower() == "y"

        cclear()

        ap_interface = wvs_input(f"Insira a sua interface. {default(AP_INTERFACE)}") or AP_INTERFACE
        ap_channel   = wvs_input(f"Insira o canal de escuta do ponto. {default(AP_CHANNEL)}") or AP_CHANNEL
        ap_driver    = wvs_input(f"Insira o identificador do driver. {default(AP_DRIVER)}") or AP_DRIVER
        ap_essid     = wvs_input(f"Insira o nome do ponto de acesso. {default(AP_ESSID)}") or AP_ESSID
        ap_phishing_service   = wvs_input(f"Escolha o serviço de phishing. {default(AP_PHISHING_SERVICE)}") or AP_PHISHING_SERVICE

        print('\n')

        AP_CREATION_GRANTED = ap_config_dump(
            ap_interface,
            ap_channel,
            ap_driver,
            ap_essid,
            ap_phishing_service
        )

        print("\n")

        if(AP_CREATION_GRANTED):
            hostapd_config_init(
                ap_interface,
                ap_channel,
                ap_driver,
                ap_essid,
                ap_phishing_service
            )

            if network_interface_ready(ap_interface):
                print_as_topic("Interface funcionando e pronta para host.")

            dnsmasq_config_init(ap_interface)
            dhcp_start()

            kill_network_processes()

            open_ap_listening(ap_interface)

            return

        warn("Operação cancelada.")

    def airscan():
        print("Varredura de rede")
        return

    def services():
        print("Lookup de serviços")
        return

    def attacks(id : str = None):
        if(id == None):
            print("Lookup de ataques")
            return

        nid = int(id)

        print(f'Lookup do ataque {nid}')
    
    return {
        WVS_AP_CREATION_ACTION: ap,
        WVS_AIRSCAN_ACTION: airscan,
        WVS_SERVICES_ACTION: services,
        WVS_ATTACKS_ACTION: attacks,
        WVS_EXITLOOP_ACTION: exit 
    }

COMMANDS = create_interface_command()

# Padrões de exibição
def table_start():
    print(f"|{cstr("red", "EVENTOS DO AP".ljust(TABLE_WIDTH, " "))}|")

def table_structure():
    print(f"|{"-" * TABLE_WIDTH}|")

def table_line(content : str):
    print(f"|{content.ljust(TABLE_WIDTH, " ")}|",)

def warn(text : str):
    print(f'{cstr("yellow", CSWARN_PREFIX)} {text}')
    print("\n")

def critical(text : str):
    print(f'{cstr("red", CSCRITICAL_PREFIX)} {text}')
    print("\n")

def print_as_topic(text : str):
    printc(
        'green', 
        CSTOPIC_PREFIX,
        end = ''
    )

    print(f' {text}')

def command_list(command, description, tab=0):
    if(tab > 0): print('    ' * tab, end="")
    printc("cyan", command, end="")
    print(f' - {description}')

def menu_banner():
    random_art_id = random.randint(0, 4)
    with open(f'ascii-arts/{random_art_id}.txt', 'r') as file:
        for line in file:
            print(line, end='')

    print("\n")

    print_as_topic("Bem-vindo ao WolveSheep: uma ferramenta brasileira Evil Twin")
    print("    ~ Extração de credenciais via phishing de serviços.")
    print("    ~ Logging detalhado de dispositivos conectados.")
    print("    ~ Acumulo e coleta de credenciais.")
    print("\n")

def basic_menu():
    print_as_topic("Inicialização")
    command_list("/ap", "defina as configuraçoes do ponto de acesso para iniciar o ataque.", 1)
    command_list("/airscan", "faça uma varredura rapida para observar pontos pela área.", 1)
    command_list("/services", "veja ID's de serviços de phishing disponiveis.", 1)
    command_list("/attacks", "recupere ista ataques anteriores (data, hora, ESSID e serviço).", 1)
    command_list("/attacks ID", "exiba o log selecionado que foi gerado durante o ataque (exemplo: /attacks 2).", 1)
    print("\n")

    printc("yellow", "Digite 'exit' para sair da ferramenta.")
    print("\n")

# Event loop e processamento de entradas
def treat_action(action : str):
    action_splitted = action.strip().split(" ")

    if(action_splitted[0] in COMMANDS):
        if(len(action_splitted) > 1):
            return {
                "action": action_splitted[0],
                "param": action_splitted[1]
            }

        return {
            "action": action_splitted[0],
            "param": None
        }

    raise WVSException(WVSERR_UNKNOWN_ACTION)
    
def wait_action():
    act_struct : dict

    try:
        act_struct = treat_action(
            input(f'{underline_string(WOLVESHEEP_WAITING)} > ')
        )
    except WVSException as error:
        raise error

    print("\n")

    if(act_struct["param"] == None):
        COMMANDS[act_struct["action"]]()
    else:
        COMMANDS[act_struct["action"]](
            act_struct["param"]
        )

    print("\n")

def cclear():
    subprocess.run(
        "cls" if SYS_INFO["osname"] == "nt" else "clear",
        shell=True
    )

# --- #
wincli_accept_ansicolor()

cclear()
menu_banner()

while(True):
    compatibility_dump()
    basic_menu()
        
    try:
        wait_action()
    except WVSException as wvse:
        warn(wvse)
