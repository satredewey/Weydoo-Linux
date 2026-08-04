import curses
import shutil
import subprocess
import sys
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BASH_DIR = SCRIPT_DIR
REPO_ROOT = SCRIPT_DIR.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from helper import *
except Exception as e:
    raise ImportError(f"Error while loading helper module: {e}")


class Install:
    def __init__(self):
        self.installed = {"flatpak": False, "chrome": False}
        self.to_install = []

        self.dependencies = {
            "chrome": ["flatpak"],
        }

        self.commands = {
            "flatpak": [
                ["sudo", "apt", "update"],
                ["sudo", "apt", "install", "-y", "flatpak"],
                ["sudo", "apt", "install", "-y", "gnome-software-plugin-flatpak"],
            ],
            "chrome": [
                [
                    "flatpak",
                    "remote-add",
                    "--if-not-exists",
                    "flathub",
                    "https://dl.flathub.org/repo/flathub.flatpakrepo",
                ],
                [
                    "flatpak",
                    "install",
                    "-y",
                    "flathub",
                    "com.google.Chrome",
                ],
            ],
        }

        self.check_installed()

    def check_installed(self):
        self.installed["flatpak"] = shutil.which("flatpak") is not None

        chrome_paths = [
            os.path.expanduser("~/.local/share/flatpak/app/com.google.Chrome"),
            "/var/lib/flatpak/app/com.google.Chrome",
            "/opt/google/chrome/chrome",
        ]

        is_chrome_installed = False
        for path in chrome_paths:
            is_chrome_installed = os.path.exists(path) or is_chrome_installed
        self.installed["chrome"] = is_chrome_installed

    def _install(self, stdscr=None, helper=None):
        if not self.to_install:
            if helper and stdscr:
                helper._show_dialog(stdscr, "You need to choose something to install.")
            return

        for item_id in list(self.to_install):
            if item_id in self.commands:
                item_success = True
                for cmd in self.commands[item_id]:
                    success, output = run_command_with_curses_exit(stdscr, cmd)
                    if not success:
                        item_success = False
                        if helper and stdscr:
                            helper._show_dialog(stdscr, f"Error: {output}")
                        break

                if item_success:
                    self.installed[item_id] = True
                    if item_id in self.to_install:
                        self.to_install.remove(item_id)

    def toggle(self, item_id):
        if item_id in self.to_install:
            self.to_install.remove(item_id)
            for child, reqs in self.dependencies.items():
                if item_id in reqs and child in self.to_install:
                    self.to_install.remove(child)
        elif self.installed[item_id] != True:
            self.to_install.append(item_id)
            for req in self.dependencies.get(item_id, []):
                if req not in self.to_install:
                    self.to_install.append(req)

        self.check_installed()

    def flatpak(self):
        self.toggle("flatpak")

    def chrome(self):
        self.toggle("chrome")


def main(stdscr):
    install = Install()
    helper = Helper(
        title="Weydoo App & Programs",
        stdscr=stdscr,
        color_enable=curses.has_colors() and curses.COLORS >= 256,
    )

    menu_meta = {"type": "choices"}
    menu = [
        {"type": "title", "text": "Install Apps & Programs"},
        {
            "type": "choice",
            "text": "Flatpak",
            "action": install.flatpak,
            "id": "flatpak",
        },
        {
            "type": "choice",
            "text": "Google Chrome",
            "action": install.chrome,
            "id": "chrome",
        },
    ]

    helper.menu(stdscr, menu, menu_meta, install)


if __name__ == "__main__":
    curses.wrapper(main)
