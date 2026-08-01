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
 ╚══╝╚══╝ ╚══════╝   ╚═╝   ╚═════╝  ╚═════╝  ╚═════╝     ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝     ╚═════╝ ╚═════╝ ╚══╝  ╚═══╝╚═╝     ╚═╝ ╚═════╝ 
                                                                                                                                            
""".strip("\n").split("\n")

translation_key = {"ok": "< OK >", "exit": "Exit"}

BASE_OPTIONS = [
    "1. Check truecolors",
    "2. Install .bashrc",
    "3. Install Eza",
    "4. Install Starship",
    "5. Install Docker",
]
BASE_OPTIONS.append(f"{len(BASE_OPTIONS) + 1}. {translation_key['exit']}")
options = list(BASE_OPTIONS)

SCRIPT_DIR = Path(__file__).resolve().parent
BASH_DIR = SCRIPT_DIR.parent
REPO_ROOT = SCRIPT_DIR.parent.parent


def run_command_with_curses_exit(stdscr, cmd):
    curses.endwin()

    if cmd[0] == "sudo" and not shutil.which("sudo"):
        real_cmd = cmd[1:]
        formatted_cmd = " ".join(f"'{arg}'" if " " in arg else arg for arg in real_cmd)
        final_cmd = ["su", "-", "-c", formatted_cmd]
        print("\n[NOTE] 'sudo' not found. Changed to 'su'.\n")
    else:
        final_cmd = cmd

    print(f"---> Executing: {' '.join(final_cmd)}\n")
    try:
        res = subprocess.run(final_cmd, check=True)
        success = res.returncode == 0
        output = "Execution succeeded"
    except subprocess.CalledProcessError as e:
        success = False
        output = f"Command failed with exit code {e.returncode}"
    except Exception as e:
        success = False
        output = str(e)

    stdscr.clear()
    curses.curs_set(0)
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
            "truecolor": curses.has_colors() and curses.COLORS >= 256,
            "bashrc": None,
            "eza": True if shutil.which("eza") else None,
            "starship": True if shutil.which("starship") else None,
            "docker": True if shutil.which("docker") else None,
        }
        self._update_options(BASE_OPTIONS)

    def _update_options(self, base_options):
        mapping = {
            0: ("truecolor", {True: "Supported", False: "Not Supported"}),
            1: ("bashrc", {True: "Installed", False: "Failed"}),
            2: ("eza", {True: "Installed", False: "Failed"}),
            3: ("starship", {True: "Installed", False: "Failed"}),
            4: ("docker", {True: "Installed", False: "Failed"}),
        }

        for idx, (key, status_map) in mapping.items():
            state = self.installed.get(key)
            if state in status_map:
                options[idx] = f"{base_options[idx]} - {status_map[state]}"
            else:
                options[idx] = base_options[idx]

    def truecolor(self, stdscr):
        stdscr.erase()
        for i, line in enumerate(title):
            draw_centered(stdscr, 1 + i, line)

        if self.installed["truecolor"]:
            draw_centered(
                stdscr,
                len(title) + 4,
                "Truecolors supported",
                curses.A_BOLD,
                1,
            )
        else:
            draw_centered(
                stdscr,
                len(title) + 4,
                "Truecolors not supported",
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
        src_path = BASH_DIR / "bashrc"
        dst_path = Path.home() / ".bashrc"

        success = False
        error_msg = ""

        if src_path.is_file():
            try:
                if dst_path.exists():
                    shutil.copy(dst_path, dst_path.with_suffix(".bak"))
                shutil.copy(src=src_path, dst=dst_path)
                success = True
                self.installed["bashrc"] = True
            except Exception as e:
                self.installed["bashrc"] = False
                error_msg = f"Error: {e}"
        else:
            self.installed["bashrc"] = False
            error_msg = f"Error: '{str(src_path)}' not found"

        self._update_options(BASE_OPTIONS)

        stdscr.erase()
        for i, line in enumerate(title):
            draw_centered(stdscr, 1 + i, line)

        if success:
            draw_centered(
                stdscr,
                len(title) + 4,
                "~/.bashrc Installed successfully!",
                curses.A_BOLD,
                1,
            )
        else:
            draw_centered(
                stdscr,
                len(title) + 4,
                "Failed to install ~/.bashrc",
                curses.A_BOLD,
                2,
            )
            draw_centered(stdscr, len(title) + 5, error_msg[: curses.COLS - 2])

        draw_centered(stdscr, len(title) + 7, translation_key["ok"], curses.A_REVERSE)
        stdscr.refresh()

        while True:
            key = stdscr.getch()
            if key in (10, 13):
                break

    def eza(self, stdscr):
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

        self.installed["eza"] = success
        self._update_options(BASE_OPTIONS)

        stdscr.erase()
        for i, line in enumerate(title):
            draw_centered(stdscr, 1 + i, line)

        if success:
            draw_centered(
                stdscr, len(title) + 4, "Eza installed successfully!", curses.A_BOLD, 1
            )
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
        draw_centered(stdscr, len(title) + 4, "Installing Starship...", curses.A_BOLD)
        stdscr.refresh()

        cmd = ["sh", "-c", "curl -sS https://starship.rs/install.sh | sh"]
        success, output = run_command_with_curses_exit(stdscr, cmd)

        if success:
            cfg_src = BASH_DIR / "starship.toml"
            cfg_dst_dir = Path.home() / ".config"
            try:
                if cfg_src.is_file():
                    cfg_dst_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy(cfg_src, cfg_dst_dir / "starship.toml")
            except Exception as e:
                output = f"Binary installed, but failed to copy config: {e}"

        self.installed["starship"] = success
        self._update_options(BASE_OPTIONS)

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

    def docker(self, stdscr):
        if self.installed["docker"] is True:
            stdscr.erase()
            for i, line in enumerate(title):
                draw_centered(stdscr, 1 + i, line)
            draw_centered(
                stdscr,
                len(title) + 4,
                "Docker is already installed on your system!",
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
                stdscr,
                [
                    "sudo",
                    "apt-get",
                    "install",
                    "-y",
                    "docker-ce",
                    "docker-ce-cli",
                    "containerd.io",
                    "docker-buildx-plugin",
                    "docker-compose-plugin",
                ],
            )

        self.installed["docker"] = success
        self._update_options(BASE_OPTIONS)

        stdscr.erase()
        for i, line in enumerate(title):
            draw_centered(stdscr, 1 + i, line)

        if success:
            draw_centered(
                stdscr,
                len(title) + 4,
                "Docker installed successfully!",
                curses.A_BOLD,
                1,
            )
        else:
            draw_centered(
                stdscr, len(title) + 4, "Failed to install Docker", curses.A_BOLD, 2
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
            key_map = {
                0: "truecolor",
                1: "bashrc",
                2: "eza",
                3: "starship",
                4: "docker",
            }
            if (
                i in key_map
                and install.installed[key_map[i]] is not None
                and install.installed["truecolor"]
            ):
                color = 1 if install.installed[key_map[i]] else 2

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
                case 5:
                    install.docker(stdscr)
                case _:
                    running = False
        elif key in (ord("q"), ord("Q")):
            running = False


if __name__ == "__main__":
    curses.wrapper(main)