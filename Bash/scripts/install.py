import curses
import shutil
import subprocess
import sys
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

BASE_OPTIONS = [
    "1. Check truecolors",
    "2. Install .bashrc",
    "3. Install Eza",
    "4. Install Starship",
]
BASE_OPTIONS.append(f"{len(BASE_OPTIONS) + 1}. {translation_key['exit']}")
options = list(BASE_OPTIONS)


def run_command_with_curses_exit(stdscr, cmd):
    """
    Quitte temporairement curses pour laisser l'utilisateur utiliser sudo / le TTY standard proprement.
    """
    curses.endwin()
    print(f"\n---> Executing: {' '.join(cmd)}\n")
    try:
        res = subprocess.run(cmd, check=True)
        success = res.returncode == 0
        output = "Execution succeeded"
    except subprocess.CalledProcessError as e:
        success = False
        output = f"Command failed with exit code {e.returncode}"
    except Exception as e:
        success = False
        output = str(e)
        
    stdscr.refresh()
    return success, output


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
        self.installed = {
            "truecolor": None,
            "bashrc": None,
            "eza": None,
            "starship": None,
        }

    def truecolor(self, stdscr):
        stdscr.erase()
        for i, line in enumerate(title):
            draw_centered(stdscr, 1 + i, line)

        if self.installed["truecolor"] is None:
            max_colors = curses.COLORS
            self.installed["truecolor"] = max_colors >= 256
            if self.installed["truecolor"]:
                draw_centered(
                    stdscr, len(title) + 4, "Truecolors supported", curses.A_BOLD, 1
                )
                options[0] = f"{BASE_OPTIONS[0]} - Supported"
            else:
                draw_centered(
                    stdscr, len(title) + 4, "Truecolors not supported", curses.A_BOLD, 2
                )
                options[0] = f"{BASE_OPTIONS[0]} - Not Supported"
        elif self.installed["truecolor"]:
            draw_centered(
                stdscr,
                len(title) + 4,
                "Truecolors already checked, supported",
                curses.A_BOLD,
                1,
            )
        else:
            draw_centered(
                stdscr,
                len(title) + 4,
                "Truecolors already checked, not supported",
                curses.A_BOLD,
                2,
            )

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
                draw_centered(
                    stdscr,
                    len(title) + 4,
                    "Truecolor not checked, do you want to check it ?",
                )

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

        script_dir = Path(__file__).resolve().parent
        candidates = [
            script_dir / "bashrc",
            script_dir.parent / "bashrc",
            script_dir.parent / "Bash" / "bashrc",
        ]

        src_path = None
        for cand in candidates:
            if cand.exists():
                src_path = cand
                break

        dst_path = Path.home() / ".bashrc"

        success = False
        error_msg = ""
        if src_path:
            try:
                if dst_path.exists():
                    shutil.copy(dst_path, dst_path.with_suffix(".bak"))
                shutil.copy(src=src_path, dst=dst_path)
                success = True
                self.installed["bashrc"] = True
                options[1] = f"{BASE_OPTIONS[1]} - Installed"
            except Exception as e:
                self.installed["bashrc"] = False
                error_msg = f"Error: {e}"
        else:
            self.installed["bashrc"] = False
            error_msg = "Error: File 'bashrc' not found in project root"

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
            draw_centered(
                stdscr,
                len(title) + 4,
                "Eza is already installed on your system!",
                curses.A_BOLD,
                1,
            )
            draw_centered(
                stdscr, len(title) + 6, translation_key["ok"], curses.A_REVERSE
            )
            stdscr.refresh()
            while True:
                if stdscr.getch() in (10, 13):
                    break
            return

        success, output = run_command_with_curses_exit(
            stdscr, ["sudo", "apt-get", "update"]
        )
        if success:
            success, output = run_command_with_curses_exit(
                stdscr, ["sudo", "apt-get", "install", "-y", "eza"]
            )
        stdscr.refresh()

        self.installed["eza"] = success

        stdscr.erase()
        for i, line in enumerate(title):
            draw_centered(stdscr, 1 + i, line)

        if success:
            draw_centered(
                stdscr, len(title) + 4, "Eza installed successfully!", curses.A_BOLD, 1
            )
            options[2] = f"{BASE_OPTIONS[2]} - Installed"
        else:
            draw_centered(
                stdscr, len(title) + 4, "Failed to install Eza", curses.A_BOLD, 2
            )
            draw_centered(stdscr, len(title) + 5, str(output)[: curses.COLS - 2])

        draw_centered(stdscr, len(title) + 7, translation_key["ok"], curses.A_REVERSE)
        stdscr.refresh()

        while True:
            key = stdscr.getch()
            if key in (10, 13):
                break

    def starship(self, stdscr):
        if shutil.which("starship"):
            self.installed["starship"] = True

        if self.installed["starship"] is True:
            stdscr.erase()
            for i, line in enumerate(title):
                draw_centered(stdscr, 1 + i, line)
            draw_centered(
                stdscr,
                len(title) + 4,
                "Starship is already installed on your system!",
                curses.A_BOLD,
                1,
            )
            draw_centered(
                stdscr, len(title) + 6, translation_key["ok"], curses.A_REVERSE
            )
            stdscr.refresh()
            while True:
                if stdscr.getch() in (10, 13):
                    break
            return

        stdscr.erase()
        for i, line in enumerate(title):
            draw_centered(stdscr, 1 + i, line)
        draw_centered(
            stdscr, len(title) + 4, "Installing Starship...", curses.A_BOLD
        )
        stdscr.refresh()

        cmd = ["sh", "-c", "curl -sS https://starship.rs/install.sh | sh"]
        success, output = run_command_with_curses_exit(stdscr, cmd)

        self.installed["starship"] = success

        stdscr.erase()
        for i, line in enumerate(title):
            draw_centered(stdscr, 1 + i, line)

        if success:
            draw_centered(
                stdscr,
                len(title) + 4,
                "Starship installed successfully!",
                curses.A_BOLD,
                1,
            )
            options[3] = f"{BASE_OPTIONS[3]} - Installed"
        else:
            draw_centered(
                stdscr, len(title) + 4, "Failed to install Starship", curses.A_BOLD, 2
            )
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
                    color = 0
            elif i == 1 and install.installed["truecolor"] is True:
                if install.installed["bashrc"] is True:
                    color = 1
                elif install.installed["bashrc"] is False:
                    color = 2
            elif i == 2 and install.installed["truecolor"] is True:
                if install.installed["eza"] is True:
                    color = 1
                elif install.installed["eza"] is False:
                    color = 2
            elif i == 3 and install.installed["truecolor"] is True:
                if install.installed["starship"] is True:
                    color = 1
                elif install.installed["starship"] is False:
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
                    install.starship(stdscr)
                case _:
                    running = False
        elif key in (ord("q"), ord("Q")):
            running = False


if __name__ == "__main__":
    curses.wrapper(main)
