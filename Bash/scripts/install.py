import curses
import shutil
import subprocess
from pathlib import Path

# --- Chemins constants ---
SCRIPT_DIR = Path(__file__).resolve().parent
BASH_DIR = SCRIPT_DIR.parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# --- Banner ASCII ---
TITLE_RAW = """
██╗    ██╗███████╗██╗   ██╗██████╗  ██████╗  ██████╗     ██████╗  █████╗ ███████╗██╗  ██╗     ██████╗ ██████╗ ███╗   ██╗███████╗██╗ ██████╗ 
██║    ██║██╔════╝╚██╗ ██╔╝██╔══██╗██╔═══██╗██╔═══██╗    ██╔══██╗██╔══██╗██╔════╝██║  ██║    ██╔════╝██╔═══██╗████╗  ██║██╔════╝██║██╔════╝ 
██║ █╗ ██║█████╗   ╚████╔╝ ██║  ██║██║   ██║██║   ██║    ██████╔╝███████║███████╗███████║    ██║     ██║   ██║██╔██╗ ██║█████╗  ██║██║  ███╗
██║███╗██║██╔══╝    ╚██╔╝  ██║  ██║██║   ██║██║   ██║    ██╔══██╗██╔══██║╚════██║██╔══██║    ██║     ██║   ██║██║╚██╗██║██╔══╝  ██║██║   ██║
╚███╔███╔╝███████╗   ██║   ██████╔╝╚██████╔╝╚██████╔╝    ██████╔╝██║  ██║███████║██║  ██║    ╚██████╗╚██████╔╝██║ ╚████║██║     ██║╚██████╔╝
 ╚══╝╚══╝ ╚══════╝   ╚═╝   ╚═════╝  ╚═════╝  ╚═════╝     ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝     ╚═════╝ ╚═════╝ ╚══╝  ╚═══╝╚═╝     ╚═╝ ╚═════╝ 
"""
title = TITLE_RAW.strip("\n").split("\n")

translation_key = {"ok": "< OK >", "exit": "Exit", "yes": "< Yes >", "no": "< No >"}

BASE_OPTIONS = [
    "1. Check truecolors",
    "2. Install .bashrc",
    "3. Install Eza",
    "4. Install Starship",
    "5. Install Docker",
    "6. Generate Docker image",
]
BASE_OPTIONS.append(f"{len(BASE_OPTIONS) + 1}. {translation_key['exit']}")
options = list(BASE_OPTIONS)


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
            "docker_image": None,
        }
        self._update_options(BASE_OPTIONS)

    def _update_options(self, base_options):
        mapping = {
            0: ("truecolor", {True: "Supported", False: "Not Supported"}),
            1: ("bashrc", {True: "Installed", False: "Failed"}),
            2: ("eza", {True: "Installed", False: "Failed"}),
            3: ("starship", {True: "Installed", False: "Failed"}),
            4: ("docker", {True: "Installed", False: "Failed"}),
            5: ("docker_image", {True: "Generated", False: "Failed"}),
        }

        for idx, (key, status_map) in mapping.items():
            state = self.installed.get(key)
            if state in status_map:
                options[idx] = f"{base_options[idx]} - {status_map[state]}"
            else:
                options[idx] = base_options[idx]

    def _show_dialog(self, stdscr, message, color_pair=0, subtext=None):
        stdscr.erase()
        for i, line in enumerate(title):
            draw_centered(stdscr, 1 + i, line)

        draw_centered(stdscr, len(title) + 4, message, curses.A_BOLD, color_pair)

        if subtext:
            draw_centered(stdscr, len(title) + 5, subtext[: curses.COLS - 2])

        draw_centered(stdscr, len(title) + 7, translation_key["ok"], curses.A_REVERSE)
        stdscr.refresh()

        while True:
            key = stdscr.getch()
            if key in (10, 13):
                break

    def _show_choice_dialog(
        self,
        stdscr,
        message,
        color_pair=0,
        subtext=None,
        yes_function=None,
        yes_args=None,
        yes_kwargs=None,
        no_function=None,
        no_args=None,
        no_kwargs=None,
    ):
        selected_option = 0
        yes_args = yes_args or ()
        yes_kwargs = yes_kwargs or {}
        no_args = no_args or ()
        no_kwargs = no_kwargs or {}

        while True:
            stdscr.erase()
            for i, line in enumerate(title):
                draw_centered(stdscr, 1 + i, line)

            draw_centered(stdscr, len(title) + 4, message, curses.A_BOLD, color_pair)

            if subtext:
                draw_centered(stdscr, len(title) + 5, subtext[: curses.COLS - 2])

            yes_attr = curses.A_REVERSE if selected_option == 0 else curses.A_NORMAL
            no_attr = curses.A_REVERSE if selected_option == 1 else curses.A_NORMAL

            max_y, max_x = stdscr.getmaxyx()
            btn_y = len(title) + 7
            spacing = 4

            total_width = (
                len(translation_key["yes"]) + spacing + len(translation_key["no"])
            )
            start_x = max(0, (max_x - total_width) // 2)

            if btn_y < max_y - 1:
                try:
                    stdscr.addstr(btn_y, start_x, translation_key["yes"], yes_attr)
                    stdscr.addstr(
                        btn_y,
                        start_x + len(translation_key["yes"]) + spacing,
                        translation_key["no"],
                        no_attr,
                    )
                except curses.error:
                    pass

            stdscr.refresh()
            key = stdscr.getch()

            if key in (curses.KEY_LEFT, curses.KEY_RIGHT, 9):  # 9 = Tab
                selected_option = 1 - selected_option
            elif key in (10, 13):  # Entrée
                if selected_option == 0:
                    if yes_function:
                        yes_function(*yes_args, **yes_kwargs)
                else:
                    if no_function:
                        no_function(*no_args, **no_kwargs)
                break
            elif key in (ord("q"), ord("Q")):
                if no_function:
                    no_function(*no_args, **no_kwargs)
                break

    def truecolor(self, stdscr):
        if self.installed["truecolor"]:
            self._show_dialog(stdscr, "Truecolors supported", color_pair=1)
        else:
            self._show_dialog(stdscr, "Truecolors not supported", color_pair=2)

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
            except Exception as e:
                error_msg = f"Error: {e}"
        else:
            error_msg = f"Error: '{src_path}' not found"

        self.installed["bashrc"] = success
        self._update_options(BASE_OPTIONS)

        if success:
            self._show_dialog(stdscr, "~/.bashrc Installed successfully!", color_pair=1)
        else:
            self._show_dialog(
                stdscr,
                "Failed to install ~/.bashrc",
                color_pair=2,
                subtext=error_msg,
            )

    def eza(self, stdscr):
        if self.installed["eza"] is True:
            self._show_dialog(
                stdscr, "Eza is already installed on your system!", color_pair=1
            )
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

        if success:
            self._show_dialog(stdscr, "Eza installed successfully!", color_pair=1)
        else:
            self._show_dialog(
                stdscr, "Failed to install Eza", color_pair=2, subtext=str(output)
            )

    def starship(self, stdscr):
        if self.installed["starship"] is True:
            self._show_dialog(
                stdscr,
                "Starship is already installed on your system!",
                color_pair=1,
            )
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

        if success:
            self._show_dialog(stdscr, "Starship installed successfully!", color_pair=1)
        else:
            self._show_dialog(
                stdscr,
                "Failed to install Starship",
                color_pair=2,
                subtext=str(output),
            )

    def docker(self, stdscr):
        if self.installed["docker"] is True:
            self._show_dialog(
                stdscr,
                "Docker is already installed on your system!",
                color_pair=1,
            )
            return

        success, output = run_command_with_curses_exit(
            stdscr, ["sh", "-c", "curl -fsSL https://get.docker.com | sh"]
        )

        self.installed["docker"] = success
        self._update_options(BASE_OPTIONS)

        if success:
            self._show_dialog(stdscr, "Docker installed successfully!", color_pair=1)
        else:
            self._show_dialog(
                stdscr,
                "Failed to install Docker",
                color_pair=2,
                subtext=str(output),
            )

    def docker_image(self, stdscr):
        if self.installed["docker"]:
            pass
        else:
            self._show_choice_dialog(
                stdscr,
                "You need to install Docker first.",
                yes_function=self.docker,
                yes_args=(stdscr,),
            )


def main(stdscr):
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
                case 6:
                    install.docker_image(stdscr)
                case _:
                    running = False
        elif key in (ord("q"), ord("Q")):
            running = False


if __name__ == "__main__":
    curses.wrapper(main)
