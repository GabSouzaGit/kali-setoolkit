from ddgs import ddgs as browser
import ddgs

from utils.clear import cs_clear
from utils.printcl import printcl, printcl_concat
from urllib.parse import urlparse

from requests import Response
import requests

session = requests.Session()
finded_urls = {}

wrld_regions = [
    "br-pt",
    "us-en",
    "wt-wt"
]

backends = [
    "bing",
    "brave",
    "duckduckgo",
    "google",
    "mojeek",
    "startpage",
    "yandex",
    "yahoo",
]

def request(page):
    href = page.get("href")

    if not href:
        return None

    if href in finded_urls: return

    finded_urls[href] = True
    parsed_url = urlparse(href)
    root = f'{parsed_url.scheme}://{parsed_url.netloc}'

    response = {
        "status_code": 404
    }

    try:
        response = session.get(
            f'{root}/robots.txt',
            allow_redirects=False
        )
    except requests.exceptions.SSLError:
        printcl("RED", "    ~ Falha na obtenção de robots.txt: falha na verificação de certificado.\n")

    except requests.exceptions.ConnectionError:
        printcl("RED", "    ~ Falha na obtenção de robots.txt: falha na conexão.\n")

    except requests.exceptions.Timeout:
        printcl("RED", "    ~ Falha na obtenção de robots.txt: endpoint demorou muito para responder.\n")

    except requests.exceptions.RequestException:
        printcl("RED", "    ~ Falha na obtenção de robots.txt: falha ao obter documento.\n")

    if type(response) != Response:
        return {
            "url": href,
            "robots.txt": {
                "status": None,
            } 
        }

    return {
        "url": href,
        "robots.txt": {
            "status": response.status_code if response.status_code == 200 else None
        }
    }

def report(report_dict):
    if(report_dict == None):
        printcl('YELLOW', '    ! - Correspondência vazia ou incompleta.\n')
        return

    print(f'    URL: {report_dict["url"]}')
    printcl_concat(
        ('DEFAULT', '    Robots.txt: '),
        ('GREEN', '200 OK\n') if report_dict["robots.txt"] != None else ('RED', 'None\n'),
    )
    
raw_entry = input(f'* Informe as palavras chaves dos sites que deseja (separe por virgula): ')

keywords = " ".join([ f'"{word.strip()}"' for word in raw_entry.split(",") ])

cs_clear()
print("Buscando na rede...\n")

for search_engine in backends:
    printcl_concat(
        ('DEFAULT', '-- Mecanismo de busca: '),
        ('GREEN', search_engine + "\n")
    )

    try:
        pages = browser.DDGS(timeout=30).text(
            f'intitle: {keywords} OR intext: {keywords} OR inurl: {keywords}',
            max_results=100,
            backend=search_engine,
            regions=wrld_regions
        )
    except ddgs.exceptions.DDGSException:
        printcl('YELLOW', '    ! - Este mecanismo não encontrou correspondências.\n')
        print(50 * "-")
        print("\n")
        continue

    for index, result in enumerate(pages, start = 1):
        response = request(result)
        report(response)

    print(50 * "-")

input("\nBusca finalizada!\nPressione ENTER para sair.")
cs_clear()