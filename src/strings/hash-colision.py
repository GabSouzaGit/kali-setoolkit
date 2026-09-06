import hashlib
import os
import subprocess
from pathlib import Path
from multiprocessing import Pool

def override(text):
    print("\033[H", end="")
    print(text, end="", flush=True)

hashing_algos = [
    hashlib.md5,
    hashlib.sha1,
    hashlib.sha224,
    hashlib.sha256,
    hashlib.sha384,
    hashlib.sha512,
    hashlib.sha3_224,
    hashlib.sha3_256,
    hashlib.sha3_384,
    hashlib.sha3_512,
    hashlib.shake_128,
    hashlib.shake_256,
]

algolist = f'\n0 - MD5\n1 - SHA1\n2 - SHA224\n3 - SHA256\n4 - SHA384\n5 - SHA512\n6 - SHA3_224\n7 - SHA3_256\n8 - SHA3_384\n9 - SHA3_512\n10 - SHAKE128\n11 - SHAKE256\n\nEscolha o algoritmo de hashing: '

def init_worker(hash, algo):
    global WORKER_HASH
    global WORKER_ALGO

    WORKER_HASH = hash
    WORKER_ALGO = algo

def chunk_generator(file, size = 10000):
    chunk = []

    for line in file:
        word = line.rstrip(b"\n")

        chunk.append(word)

        if(len(chunk) >= size):
            yield chunk
            chunk = []
        
    if chunk: yield chunk

def define_workers():
    cpus = os.cpu_count()

    if(cpus <= 4):
        return cpus // 2
    if(cpus > 4 and cpus <= 6): return 4
    if(cpus >= 8): return 6

def hash_cracker(chunk):
    candidates = []

    for word in chunk:
        hash_comp = hashing_algos[WORKER_ALGO](word).digest()

        if(hash_comp == WORKER_HASH): candidates.append(word)

    return candidates, len(chunk)

print(f"CPUS disponiveis: {os.cpu_count()}")

if __name__ == '__main__':
    hash = bytes.fromhex(input(f'Informe a hash: ').strip())
    algo = int(input(algolist))
    path = Path(input(f'\nInforme o caminho das wordlists: ').strip())
    workers_qtd = define_workers()
    results = []
    process_tracker = 0

    subprocess.run("cls", shell=True)

    for file in path.iterdir():
        if file.suffix != ".txt": continue

        with open(path / file.name, "rb") as wordlist:
            chunks = chunk_generator(wordlist)

            with Pool(
                    processes=workers_qtd,
                    initializer=init_worker,
                    initargs=(hash, algo)
                ) as pool:
                for candidates, processed in pool.imap_unordered(
                    hash_cracker,
                    chunks
                ):
                    process_tracker += processed
                    print(f"Chunks processadas: {process_tracker}")
                    results.extend(candidates)

    print("Processamento concluido. Colisões identificadas:\n")

    for result in results:
        print(result.decode('utf-8'))
    
    input("\nPressione ENTER para sair")
