import curses
import pyfiglet


class Helper:
    def __init__(self, title, stdscr=None, color_enable=False):
        if stdscr is None:
            stdscr = curses.initscr()

        curses.start_color()
        curses.use_default_colors()
        curses.curs_set(0)

        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_RED, -1)
        curses.init_pair(3, curses.COLOR_BLUE, -1)
        curses.color_pair(curses.COLOR_BLACK)

        _, max_x = stdscr.getmaxyx()

        self.title = (
            pyfiglet.figlet_format(
                str(title),
                font="ansi_shadow",
                width=max_x,
            )
            .rstrip("\n")
            .split("\n")
        )
        self.color_enable = color_enable

    def _draw_centered(self, stdscr, y, text, attr=curses.A_NORMAL, color_pair=0):
        max_y, max_x = stdscr.getmaxyx()
        if not self.color_enable:
            color_pair = 0

        if y < max_y - 1:
            x = max(0, (max_x - len(text)) // 2)
            try:
                full_attr = attr | curses.color_pair(color_pair)
                stdscr.addnstr(y, x, text, max_x - x - 1, full_attr)
            except curses.error:
                pass

    def _draw_menu(self, stdscr, menu, current_selectable_idx, options_class=None):
        stdscr.erase()

        for i, line in enumerate(self.title):
            self._draw_centered(stdscr, y=(i + 1), text=line)

        start_y = len(self.title) + 3
        selectable_counter = 0

        for i, item in enumerate(menu):
            y_pos = start_y + i
            item_type = item.get("type")

            if item_type == "title":
                self._draw_centered(
                    stdscr,
                    y=y_pos,
                    text=f"--- {item['text']} ---",
                    attr=curses.A_BOLD,
                    color_pair=3,
                )
            elif item_type == "spacer":
                self._draw_centered(
                    stdscr,
                    y=y_pos,
                    text="",
                )
            else:
                is_selected = selectable_counter == current_selectable_idx
                label = item.get("text", "")

                item_id = str(item.get("id", ""))
                installed = None
                if options_class and hasattr(options_class, "installed"):
                    if options_class.installed.get(item_id) is True:
                        label += " - Installed"
                        installed = True
                    elif options_class.installed.get(item_id) is False:
                        label += " - Failed"
                        installed = False

                if is_selected:
                    text_to_display = f"> {label} <"
                    attr = curses.A_BOLD | curses.A_REVERSE
                else:
                    text_to_display = f"  {label}  "
                    attr = curses.A_NORMAL

                self._draw_centered(
                    stdscr,
                    y=y_pos,
                    text=text_to_display,
                    attr=attr,
                    color_pair=(
                        1 if installed == True else 2 if installed == False else 0
                    ),
                )

                selectable_counter += 1

        stdscr.refresh()

    def _show_dialog(self, stdscr, message, color_pair=0, subtext=None):
        stdscr.erase()
        for i, line in enumerate(self.title):
            self._draw_centered(stdscr, 1 + i, line)

        self._draw_centered(
            stdscr,
            len(self.title) + 4,
            message,
            curses.A_BOLD,
            color_pair if self.color_enable else 0,
        )

        if subtext:
            self._draw_centered(stdscr, len(self.title) + 5, subtext[: curses.COLS - 2])

        self._draw_centered(stdscr, len(self.title) + 7, "--- OK ---", curses.A_REVERSE)
        stdscr.refresh()

        while True:
            key = stdscr.getch()
            if key in (10, 13):
                break

    def _show_text(self, stdscr, message, color_pair=0, subtext=None):
        stdscr.erase()
        for i, line in enumerate(self.title):
            self._draw_centered(stdscr, 1 + i, line)

        self._draw_centered(
            stdscr,
            len(self.title) + 4,
            message,
            curses.A_BOLD,
            color_pair if self.color_enable else 0,
        )

        if subtext:
            self._draw_centered(stdscr, len(self.title) + 5, subtext[: curses.COLS - 2])

        stdscr.refresh()

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

        if yes_args is not None and not isinstance(yes_args, (tuple, list)):
            yes_args = (yes_args,)
        else:
            yes_args = yes_args or ()

        if no_args is not None and not isinstance(no_args, (tuple, list)):
            no_args = (no_args,)
        else:
            no_args = no_args or ()

        yes_kwargs = yes_kwargs or {}
        no_kwargs = no_kwargs or {}

        while True:
            stdscr.erase()
            for i, line in enumerate(self.title):
                self._draw_centered(stdscr, 1 + i, line)

            self._draw_centered(
                stdscr, len(self.title) + 4, message, curses.A_BOLD, color_pair
            )

            if subtext:
                self._draw_centered(
                    stdscr, len(self.title) + 5, subtext[: curses.COLS - 2]
                )

            yes_attr = curses.A_REVERSE if selected_option == 0 else curses.A_NORMAL
            no_attr = curses.A_REVERSE if selected_option == 1 else curses.A_NORMAL

            max_y, max_x = stdscr.getmaxyx()
            btn_y = len(self.title) + 7
            spacing = 4

            total_width = len("< Yes >") + spacing + len("< No >")
            start_x = max(0, (max_x - total_width) // 2)

            if btn_y < max_y - 1:
                try:
                    stdscr.addstr(btn_y, start_x, "< Yes >", yes_attr)
                    stdscr.addstr(
                        btn_y,
                        start_x + len("< Yes >") + spacing,
                        "< No >",
                        no_attr,
                    )
                except curses.error:
                    pass

            stdscr.refresh()
            key = stdscr.getch()

            if key in (curses.KEY_LEFT, curses.KEY_RIGHT, 9):
                selected_option = 1 - selected_option
            elif key in (10, 13):
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

    def stop(self):
        self.running = False

    def menu(self, stdscr, menu=None, options_class=None):
        if menu is None:
            menu = []

        menu.append({"type": "spacer"})
        menu.append({"type": "option", "text": "Exit", "action": self.stop})

        selectable_items = [
            item for item in menu if item.get("type") not in ("title", "spacer")
        ]
        if not selectable_items:
            return None

        current_option = 0
        self.running = True

        while self.running:
            self._draw_menu(stdscr, menu, current_option, options_class)
            key = stdscr.getch()

            if key == curses.KEY_UP:
                current_option = (current_option - 1) % len(selectable_items)
            elif key == curses.KEY_DOWN or key in (9, ord("\t")):
                current_option = (current_option + 1) % len(selectable_items)
            elif key in (10, 13):
                selected_item = selectable_items[current_option]
                if "action" in selected_item and callable(selected_item["action"]):
                    args = selected_item.get("action_args", ())
                    if not isinstance(args, (list, tuple)):
                        args = (args,)
                    selected_item["action"](*args)
            elif key == ord("c"):
                self.color_enable = not self.color_enable
            elif key == ord("q"):
                self.running = False

        return None
