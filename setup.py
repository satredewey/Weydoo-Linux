import os
import sys
import subprocess

if not os.path.exists(".venv"):
    subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)

venv_python = os.path.join(".venv", "bin", "python")
venv_pip = os.path.join(".venv", "bin", "pip")

subprocess.run([venv_pip, "install", "pyfiglet"], check=True)

if sys.executable != os.path.abspath(venv_python):
    os.execv(venv_python, [venv_python] + sys.argv)

import pyfiglet

print(pyfiglet.figlet_format("Succes !", font="ansi_shadow"))
print("\nRun 'source .venv/bin/activate' before runnings scripts.")