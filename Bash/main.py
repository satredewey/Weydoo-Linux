import curses
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BASH_DIR = SCRIPT_DIR
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from helper import *
    except Exception as e:
        raise(f"Error while loading helper module: {e}")
else:
    raise("Error while loading helper module")



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

    # Update Done
    def truecolor(self, stdscr=curses.initscr, helper=Helper):
        if self.installed["truecolor"]:
            helper._show_dialog(stdscr, "Truecolors supported", color_pair=1)
        else:
            helper._show_dialog(stdscr, "Truecolors not supported", color_pair=2)

    # Update DONE
    def bashrc(self, stdscr=curses.initscr, helper=Helper):
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

        helper._show_dialog(
            stdscr=stdscr,
            message=".bashrc installed.",
            subtext="Run 'source ~/.bashrc' to apply",
        )

    # Update DONE
    def eza(self, stdscr=curses.initscr, helper=Helper):
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

        if success:
            helper._show_dialog(stdscr, "Eza installed successfully!", color_pair=1)
        else:
            helper._show_dialog(
                stdscr, "Failed to install Eza", color_pair=2, subtext=str(output)
            )

    # Update DONE
    def starship(self, stdscr=curses.initscr, helper=Helper):
        if self.installed["starship"] is True:
            helper._show_dialog(
                stdscr,
                "Starship is already installed on your system!",
                color_pair=1,
            )
            return

        helper._show_text(stdscr, "Installing Starship...")

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

        if success:
            helper._show_dialog(
                stdscr, "Starship installed successfully!", color_pair=1
            )
        else:
            helper._show_dialog(
                stdscr,
                "Failed to install Starship",
                color_pair=2,
                subtext=str(output),
            )

    # Update DONE
    def docker(self, stdscr=curses.initscr, helper=Helper):
        if self.installed["docker"] is True:
            helper._show_dialog(
                stdscr,
                "Docker is already installed on your system!",
                color_pair=1,
            )
            return

        success, output = run_command_with_curses_exit(
            stdscr, ["sh", "-c", "curl -fsSL https://get.docker.com | sh"]
        )

        self.installed["docker"] = success

        if success:
            helper._show_dialog(stdscr, "Docker installed successfully!", color_pair=1)
        else:
            helper._show_dialog(
                stdscr,
                "Failed to install Docker",
                color_pair=2,
                subtext=str(output),
            )

    # Update Done
    def docker_image(self, stdscr=curses.initscr, helper=Helper):
        if shutil.which("docker"):
            self.installed["docker"] = True

        if self.installed["docker"]:
            helper._show_text(stdscr, "Starting Docker daemon...")
    
            if shutil.which("service"):
                run_command_with_curses_exit(stdscr, ["sudo", "service", "docker", "start"])
            elif shutil.which("systemctl"):
                run_command_with_curses_exit(stdscr, ["sudo", "systemctl", "start", "docker"])
            else:
                helper._show_dialog(stdscr, "Can't start Docker deamon.")
                return

            cmd = ["sudo", "docker", "build", "-t", "temp-ubuntu", str(BASH_DIR)]
            
            success, output = run_command_with_curses_exit(stdscr, cmd)
            self.installed["docker_image"] = success

            if success:
                helper._show_dialog(
                    stdscr, "Docker image generated successfully!", color_pair=1
                )
            else:
                helper._show_dialog(
                    stdscr,
                    "Failed to generate Docker image",
                    color_pair=2,
                    subtext=str(output),
                )
        else:
            def install_and_retry():
                self.docker(stdscr, helper)
                if self.installed["docker"]:
                    self.docker_image(stdscr, helper)

            helper._show_choice_dialog(
                stdscr,
                "You need to install Docker first.",
                subtext="Do you want to install Docker now?",
                yes_function=install_and_retry,
            )


def main(stdscr=curses.initscr()):
    install = Install()
    helper = Helper(
        title="Weydoo Bash Config",
        stdscr=stdscr,
        color_enable=install.installed["truecolor"],
    )

    menu_meta = {
        "type": "steps"
    }
    menu = [
        {"type": "title", "text": "Programs"},
        {
            "type": "option",
            "text": "Install Starship",
            "action": install.starship,
            "action_args": [stdscr, helper],
            "id": "starship",
        },
        {
            "type": "option",
            "text": "Eza",
            "action": install.eza,
            "action_args": [stdscr, helper],
            "id": "eza"
        },
        {
            "type": "option",
            "text": "Docker",
            "action": install.docker,
            "action_args": [stdscr, helper],
            "id": "docker"
        },
        {"type": "spacer"},
        {"type": "title", "text": "Configs"},
        {
            "type": "option",
            "text": ".bashrc",
            "action": install.bashrc,
            "action_args": [stdscr, helper],
            "id": "bashrc"
        },
        {
            "type": "option",
            "text": "Make docker image",
            "action": install.docker_image,
            "action_args": [stdscr, helper],
            "id": "docker_image"
        }
    ]

    helper.menu(stdscr, menu, install)


if __name__ == "__main__":
    curses.wrapper(main)
