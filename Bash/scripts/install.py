import curses
import shutil
import subprocess
from pathlib import Path

title = """
██╗    ██╗███████╗██╗   ██╗██████╗  ██████╗  ██████╗     ██████╗  █████╗ ███████╗██╗  ██╗     ██████╗ ██████╗ ███╗   ██╗███████╗██╗ ██████╗ 
██║    ██║██╔════╝╚██╗ ██╔╝██╔══██╗██╔═══██╗██╔═══██╗    ██╔══██╗██╔══██╗██╔════╝██║  ██║    ██╔════╝██╔═══██╗████╗  ██║██╔════╝██║██╔════╝ 
██║ █╗ ██║█████╗   ╚████╔╝ ██║  ██║██║   ██║██║   ██║    ██████╔╝███████║███████╗███████║    ██║     ██║   ██║██╔██╗ ██║█████╗  ██║██║  ███╗
██║███╗██║██╔══╝    ╚██╔╝  ██║  ██║██║   ██║██║   ██║    ██╔══██╗██╔══██║╚════██║██╔══██║    ██║     ██║   ██║██║╚██╗██║██╔══╝  ██║██║   ██║
╚███╔███╔╝███████╗   ██║   ██████╔╝╚██████╔╝╚██████╔╝    ██████╔╝██║  ██║███████║██║  ██║    ╚██████╗╚██████╔╝██║ ╚████║██║     ██║╚██████╔╝
 ╚══╝╚══╝ ╚══════╝   ╚═╝   ╚═════╝  ╚═════╝  ╚═════╝     ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝     ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝ ╚═════╝ 
                                                                                                                                            
"""
translation_key = {"ok": "< OK >", "exit": "Exit"}

BASE_OPTIONS = ["1. Check truecolors", "2. Install .bashrc", "3. Install Eza", f"4. {translation_key['exit']}"]
options = list(BASE_OPTIONS)


def exec_sudo_command_in_curses(password, cmd):
    full_cmd = ["sudo", "-S"] + cmd
    res = subprocess.run(
        full_cmd,
        input=f"{password}\n",
        capture_output=True,
        text=True
    )
    return res.returncode == 0, res.stdout or res.stderr


def get_password(stdscr):
    stdscr.erase()
    for i, line in enumerate(title):
        draw_centered(stdscr, 1 + i, line)

    curses.echo(False)
    draw_centered(stdscr, len(title) + 3, "Enter Sudo Password: ", curses.A_BOLD)
    stdscr.refresh()

    pwd = []
    while True:
        ch = stdscr.getch()
        if ch in (10, 13):  # Entrée
            break
        elif ch in (curses.KEY_BACKSPACE, 127, 8):
            if pwd:
                pwd.pop()
                y, x = stdscr.getyx()
                stdscr.move(y, x - 1)
                stdscr.delch()
        elif ch in (ord('q'), ord('Q')) and not pwd:
            return None
        elif 32 <= ch <= 126:  # Caractères imprimables
            pwd.append(chr(ch))
            stdscr.addch('*')
        stdscr.refresh()

    return "".join(pwd)


def draw_centered(stdscr, y, text, attr=curses.A_NORMAL, color_pair=0):
    max_y, max_x = stdscr.getmaxyx()
    if y < max_y - 1:
        x = max(0, (max_x - len(text)) // 2)
        try:
            full_attr = attr | curses.color_pair(color_pair)
            stdscr.addstr(y, x, text[: max_x - 1], full_attr)
        except curses.error:
            pass


class Install:
    def __init__(self):
        self.installed = {"truecolor": None, "bashrc": None, "eza": None}

    def truecolor(self, stdscr):
        stdscr.erase()
        for i, line in enumerate(title):
            draw_centered(stdscr, 1 + i, line)

        if self.installed["truecolor"] is None:
            max_colors = curses.COLORS
            self.installed["truecolor"] = max_colors >= 256
            if self.installed["truecolor"]:
                draw_centered(stdscr, len(title) + 4, "Truecolors supported", curses.A_BOLD, 1)
                options[0] = f"{BASE_OPTIONS[0]} - Supported"
            else:
                draw_centered(stdscr, len(title) + 4, "Truecolors not supported", curses.A_BOLD, 2)
                options[0] = f"{BASE_OPTIONS[0]} - Not Supported"
        elif self.installed["truecolor"]:
            draw_centered(stdscr, len(title) + 4, "Truecolors already checked, supported", curses.A_BOLD, 1)
        else:
            draw_centered(stdscr, len(title) + 4, "Truecolors already checked, not supported", curses.A_BOLD, 2)

        draw_centered(stdscr, len(title) + 6, translation_key["ok"], curses.A_REVERSE)
        stdscr.refresh()

        while True:
            key = stdscr.getch()
            if key in (10, 13):
                break

    def bashrc(self, stdscr):
        if self.installed["truecolor"] is None:
            current_option = 0
            while True:
                stdscr.erase()
                for i, line in enumerate(title):
                    draw_centered(stdscr, 1 + i, line)
                draw_centered(stdscr, len(title) + 4, "Truecolor not checked, do you want to check it ?")

                for i, option in enumerate(["< Yes >", "< No >"]):
                    attr = curses.A_REVERSE if i == current_option else curses.A_NORMAL
                    draw_centered(stdscr, len(title) + 6 + i, option, attr)

                stdscr.refresh()
                key = stdscr.getch()

                if key == curses.KEY_UP:
                    current_option = (current_option - 1) % 2
                elif key == curses.KEY_DOWN:
                    current_option = (current_option + 1) % 2
                elif key in (10, 13):
                    if current_option == 0:
                        self.truecolor(stdscr)
                    break
                elif key in (ord("q"), ord("Q")):
                    return

        src_path = Path(__file__).resolve().parent / "../bashrc"
        dst_path = Path.home() / ".bashrc"

        success = False
        try:
            shutil.copy(src=src_path, dst=dst_path)
            success = True
            self.installed["bashrc"] = True
        except Exception as e:
            self.installed["bashrc"] = False
            error_msg = f"Error: {e}"

        stdscr.erase()
        for i, line in enumerate(title):
            draw_centered(stdscr, 1 + i, line)

        if success:
            draw_centered(
                stdscr,
                len(title) + 4,
                "~/.bashrc Installed successfully!",
                curses.A_BOLD,
                1 if self.installed["truecolor"] is True else 0,
            )
        else:
            draw_centered(
                stdscr,
                len(title) + 4,
                "Failed to install ~/.bashrc",
                curses.A_BOLD,
                2 if self.installed["truecolor"] is True else 0,
            )
            draw_centered(stdscr, len(title) + 5, error_msg[: curses.COLS - 2])

        draw_centered(stdscr, len(title) + 7, translation_key["ok"], curses.A_REVERSE)
        stdscr.refresh()

        while True:
            key = stdscr.getch()
            if key in (10, 13):
                break

    def eza(self, stdscr):
        if shutil.which("eza"):
            self.installed["eza"] = True

        if self.installed["eza"] is True:
            stdscr.erase()
            for i, line in enumerate(title):
                draw_centered(stdscr, 1 + i, line)
            draw_centered(stdscr, len(title) + 4, "Eza is already installed on your system!", curses.A_BOLD, 1)
            draw_centered(stdscr, len(title) + 6, translation_key["ok"], curses.A_REVERSE)
            stdscr.refresh()
            while True:
                if stdscr.getch() in (10, 13):
                    break
            return

        password = get_password(stdscr)
        if not password:
            return

        stdscr.erase()
        for i, line in enumerate(title):
            draw_centered(stdscr, 1 + i, line)
        draw_centered(stdscr, len(title) + 4, "Installing Eza via APT...", curses.A_BOLD)
        stdscr.refresh()

        exec_sudo_command_in_curses(password, ["apt-get", "update", "-y"])
        success, output = exec_sudo_command_in_curses(password, ["apt-get", "install", "-y", "eza"])

        self.installed["eza"] = success

        stdscr.erase()
        for i, line in enumerate(title):
            draw_centered(stdscr, 1 + i, line)

        if success:
            draw_centered(stdscr, len(title) + 4, "Eza installed successfully!", curses.A_BOLD, 1)
            options[2] = f"{BASE_OPTIONS[2]} - Installed"
        else:
            draw_centered(stdscr, len(title) + 4, "Failed to install Eza", curses.A_BOLD, 2)
            draw_centered(stdscr, len(title) + 5, str(output)[: curses.COLS - 2])

        draw_centered(stdscr, len(title) + 7, translation_key["ok"], curses.A_REVERSE)
        stdscr.refresh()

        while True:
            key = stdscr.getch()
            if key in (10, 13):
                break


def main(stdscr):
    global title
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)

    title = title.strip("\n").split("\n")
    current_option = 0
    running = True

    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)

    install = Install()

    while running:
        stdscr.erase()

        for i, line in enumerate(title):
            draw_centered(stdscr, 1 + i, line)

        for i, option in enumerate(options):
            attr = curses.A_REVERSE if i == current_option else curses.A_NORMAL

            color = 0
            if i == 0:
                if install.installed["truecolor"] is True:
                    color = 1
                elif install.installed["truecolor"] is False:
                    color = 2
            elif i == 1:
                if install.installed["bashrc"] is True:
                    color = 1
                elif install.installed["bashrc"] is False:
                    color = 2
            elif i == 2:
                if install.installed["eza"] is True:
                    color = 1
                elif install.installed["eza"] is False:
                    color = 2

            draw_centered(stdscr, len(title) + 3 + i, option, attr, color)

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_option = (current_option - 1) % len(options)
        elif key == curses.KEY_DOWN:
            current_option = (current_option + 1) % len(options)
        elif key in (10, 13):
            match current_option + 1:
                case 1:
                    install.truecolor(stdscr)
                case 2:
                    install.bashrc(stdscr)
                case 3:
                    install.eza(stdscr)
                case 4:
                    running = False
                case _:
                    pass
        elif key in (ord("q"), ord("Q")):
            running = False


if __name__ == "__main__":
    curses.wrapper(main)