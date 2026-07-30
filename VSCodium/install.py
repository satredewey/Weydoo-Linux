import curses
import shutil
import sys
from pathlib import Path

# https://patorjk.com/software/taag/#p=display&f=ANSI+Shadow
title = """
██╗    ██╗███████╗██╗   ██╗██████╗  ██████╗  ██████╗     ██╗   ██╗███████╗ ██████╗ ██████╗ ██████╗ ██╗██╗   ██╗███╗   ███╗     ██████╗ ██████╗ ███╗   ██╗███████╗██╗ ██████╗ 
██║    ██║██╔════╝╚██╗ ██╔╝██╔══██╗██╔═══██╗██╔═══██╗    ██║   ██║██╔════╝██╔════╝██╔═══██╗██╔══██╗██║██║   ██║████╗ ████║    ██╔════╝██╔═══██╗████╗  ██║██╔════╝██║██╔════╝ 
██║ █╗ ██║█████╗   ╚████╔╝ ██║  ██║██║   ██║██║   ██║    ██║   ██║███████╗██║     ██║   ██║██║  ██║██║██║   ██║██╔████╔██║    ██║     ██║   ██║██╔██╗ ██║█████╗  ██║██║  ███╗
██║███╗██║██╔══╝    ╚██╔╝  ██║  ██║██║   ██║██║   ██║    ╚██╗ ██╔╝╚════██║██║     ██║   ██║██║  ██║██║██║   ██║██║╚██╔╝██║    ██║     ██║   ██║██║╚██╗██║██╔══╝  ██║██║   ██║
╚███╔███╔╝███████╗   ██║   ██████╔╝╚██████╔╝╚██████╔╝     ╚████╔╝ ███████║╚██████╗╚██████╔╝██████╔╝██║╚██████╔╝██║ ╚═╝ ██║    ╚██████╗╚██████╔╝██║ ╚████║██║     ██║╚██████╔╝
 ╚══╝╚══╝ ╚══════╝   ╚═╝   ╚═════╝  ╚═════╝  ╚═════╝       ╚═══╝  ╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚═╝ ╚═════╝ ╚═╝     ╚═╝     ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝ ╚═════╝ 
"""
options = ["< Yes >", "< No >"]


def draw_centered(stdscr, y, text, attr=curses.A_NORMAL, color_pair=0):
    max_y, max_x = stdscr.getmaxyx()
    if y < max_y - 1:
        x = max(0, (max_x - len(text)) // 2)
        try:
            full_attr = attr | curses.color_pair(color_pair)
            stdscr.addstr(y, x, text[: max_x - 1], full_attr)
        except curses.error:
            pass


def main(stdscr):
    global title
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)

    title_lines = title.strip("\n").split("\n")
    current_option = 0
    running = True

    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)

    while running:
        stdscr.erase()
        for i, line in enumerate(title_lines):
            draw_centered(stdscr, 1 + i, line)

        for i, option in enumerate(options):
            attr = curses.A_REVERSE if i == current_option else curses.A_NORMAL
            draw_centered(stdscr, len(title_lines) + 3 + i, option, attr, i + 1)

        stdscr.refresh()
        key = stdscr.getch()

        if key in (curses.KEY_UP, ord("k"), ord("z")) and current_option > 0:
            current_option -= 1
        elif key in (curses.KEY_DOWN, ord("j"), ord("s")) and current_option < 1:
            current_option += 1
        elif key in (10, 13):
            match current_option + 1:
                case 1:
                    src_dir = Path(__file__).resolve().parent
                    dst_dir = Path.home() / ".config" / "VSCodium" / "User"

                    error_msg = ""
                    copied_files = 0

                    try:
                        dst_dir.mkdir(parents=True, exist_ok=True)
                        json_files = list(src_dir.glob("*.json"))

                        if not json_files:
                            raise FileNotFoundError(
                                "Aucun fichier .json trouvé dans le dossier du script"
                            )

                        for json_file in json_files:
                            shutil.copy(src=json_file, dst=dst_dir / json_file.name)
                            copied_files += 1

                    except Exception as e:
                        error_msg = f"Erreur : {e}"

                    stdscr.erase()
                    for i, line in enumerate(title_lines):
                        draw_centered(stdscr, 1 + i, line)

                    if copied_files > 0 and not error_msg:
                        draw_centered(
                            stdscr,
                            len(title_lines) + 4,
                            f"VSCodium Config Installed ({copied_files} file(s)) !",
                            curses.A_BOLD,
                            1,
                        )
                    else:
                        draw_centered(
                            stdscr,
                            len(title_lines) + 4,
                            "Error when installing VSCodium Config",
                            curses.A_BOLD,
                            2,
                        )
                        if error_msg:
                            draw_centered(
                                stdscr,
                                len(title_lines) + 5,
                                error_msg[: curses.COLS - 2],
                            )

                    draw_centered(
                        stdscr, len(title_lines) + 7, "< OK >", curses.A_REVERSE
                    )

                    stdscr.refresh()
                    while True:
                        k = stdscr.getch()
                        if k in (10, 13, 27):
                            break
                    
                    running = False

                case 2:
                    running = False
        elif key in (ord("q"), ord("Q"), 27):
            running = False


if __name__ == "__main__":
    curses.wrapper(main)
