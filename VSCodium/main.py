import curses
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
VSCODIUM_DIR = SCRIPT_DIR
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from helper import *
    except Exception as e:
        raise(f"Error while loading helper module: {e}")
else:
    raise("Error while loading helper module")


def install(stdscr, helper: Helper):
    src_dir = VSCODIUM_DIR
    dst_dir = Path.home() / ".config" / "VSCodium" / "User"

    copied_files = 0

    try:
        dst_dir.mkdir(parents=True, exist_ok=True)
        json_files = list(src_dir.glob("*.json"))

        if not json_files:
            raise FileNotFoundError("No .json file found in the script folder")

        for json_file in json_files:
            shutil.copy(src=json_file, dst=dst_dir / json_file.name)
            copied_files += 1

        helper._show_dialog(
            stdscr,
            f"VSCodium Config Installed ({copied_files} file(s))!",
            color_pair=1,
        )

    except Exception as e:
        helper._show_dialog(
            stdscr,
            "Error when installing VSCodium Config",
            color_pair=2,
            subtext=str(e),
        )


def main(stdscr):
    helper = Helper(
        title="Weydoo VSCodium Config",
        stdscr=stdscr,
        color_enable=curses.has_colors() and curses.COLORS >= 256,
    )

    helper._show_choice_dialog(
        stdscr,
        "Do you want to install the VSCodium Config ?",
        yes_function=install,
        yes_args=(stdscr, helper),
        no_function=lambda: None,
    )


if __name__ == "__main__":
    curses.wrapper(main)