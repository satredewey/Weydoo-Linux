import os
import sys
import subprocess

if not os.path.exists(".venv"):
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
    except subprocess.CalledProcessError:
        print("The venv extension is missing, installing via apt...")
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y", "python3-venv"], check=True)
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)

venv_python = os.path.join(".venv", "bin", "python")
venv_pip = os.path.join(".venv", "bin", "pip")

subprocess.run([venv_pip, "install", "pyfiglet"], check=True)

if sys.executable != os.path.abspath(venv_python):
    os.execv(venv_python, [venv_python] + sys.argv)

import pyfiglet
print(pyfiglet.figlet_format("Succes !", font="ansi_shadow"))
print("Run 'source .venv/bin/activate' before running scripts.")