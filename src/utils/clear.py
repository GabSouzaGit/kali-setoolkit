import subprocess
import os

def cs_clear():
    subprocess.run("cls" if os.name == "nt" else "clear", shell=True)