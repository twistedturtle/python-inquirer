from readchar import key

from inquirer import errors
from inquirer.render.console._other import GLOBAL_OTHER_CHOICE
from inquirer.render.console.base import MAX_OPTIONS_DISPLAYED_AT_ONCE
from inquirer.render.console.base import BaseConsoleRender
from inquirer.render.console.base import half_options

from inquirer.render.console._columnise import (
    get_colwidths,
    Option,
)


class List(BaseConsoleRender):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current = self._current_index()

    @property
    def is_long(self):
        choices = self.question.choices or []
        return len(choices) >= MAX_OPTIONS_DISPLAYED_AT_ONCE

    def get_hint(self):
        try:
            choice = self.question.choices[self.current]
            hint = self.question.hints[choice]
            if hint:
                return f"{choice}: {hint}"
            else:
                return f"{choice}"
        except (KeyError, IndexError):
            return ""

    def get_options(self):
        choices = self.question.choices or []
        if self.is_long:
            cmin = 0
            cmax = MAX_OPTIONS_DISPLAYED_AT_ONCE

            if half_options < self.current < len(choices) - half_options:
                cmin += self.current - half_options
                cmax += self.current - half_options
            elif self.current >= len(choices) - half_options:
                cmin += len(choices) - MAX_OPTIONS_DISPLAYED_AT_ONCE
                cmax += len(choices)

            cchoices = choices[cmin:cmax]
        else:
            cchoices = choices

        ending_milestone = max(len(choices) - half_options, half_options + 1)
        is_in_beginning = self.current <= half_options
        is_in_middle = half_options < self.current < ending_milestone
        is_in_end = self.current >= ending_milestone

        for index, choice in enumerate(cchoices):
            end_index = ending_milestone + index - half_options - 1
            if (
                (is_in_middle and index == half_options)
                or (is_in_beginning and index == self.current)
                or (is_in_end and end_index == self.current)
            ):
                color = self.theme.List.selection_color
                symbol = "+" if choice == GLOBAL_OTHER_CHOICE else self.theme.List.selection_cursor
            else:
                color = self.theme.List.unselected_color
                symbol = " " if choice == GLOBAL_OTHER_CHOICE else " " * len(self.theme.List.selection_cursor)
            yield choice, symbol, color

    def process_input(self, pressed):
        question = self.question
        if pressed == key.UP:
            if question.carousel and self.current == 0:
                self.current = len(question.choices) - 1
            else:
                self.current = max(0, self.current - 1)
            return
        if pressed == key.DOWN:
            if question.carousel and self.current == len(question.choices) - 1:
                self.current = 0
            else:
                self.current = min(len(self.question.choices) - 1, self.current + 1)
            return
        if pressed == key.ENTER:
            value = self.question.choices[self.current]

            if value == GLOBAL_OTHER_CHOICE:
                value = self.other_input()
                if not value:
                    # Clear the print inquirer.text made, since the user didn't enter anything
                    print(self.terminal.move_up + self.terminal.clear_eol, end="")
                    return

            raise errors.EndOfInput(getattr(value, "value", value))

        if pressed == key.CTRL_C:
            raise KeyboardInterrupt()

    def _current_index(self):
        try:
            return self.question.choices.index(self.question.default)
        except ValueError:
            return 0


class List2(BaseConsoleRender):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current = self._current_index()

        q = self.question
        t = self.theme.options
        self.hsort = self._get_option(q.hsort, t.hsort, False)
        self.arrangement = self._get_option(q.arrangement, t.arrangement, "vert")
        self.paddingsize = self._get_option(q.pad_size, t.pad_size, 2)

        self.process_options(self.hsort)
        self.cur_row, self.cur_col = self._reverseindex(self.current)

    @property
    def is_long(self):
        choices = self.question.choices or []
        return len(choices) >= MAX_OPTIONS_DISPLAYED_AT_ONCE

    def process_options(self, hsort=False):
        self.options = [Option(x) for x in self.question.choices]

        prefix_size = len(self.theme.List.selection_cursor) + 1

        self.nrows, self.ncols, self.colwidths = get_colwidths(
            self.options, prefix_size, self.paddingsize, hsort=self.hsort, arrangement=self.arrangement
        )  # , displaywidth)

    def _reverseindex(self, i):
        if self.hsort:
            row = i // self.ncols
            col = i % self.nrows
            return row, col

        row = i % self.ncols
        col = i // self.nrows
        return row, col

    def _index(self, row, col):
        if self.hsort:
            return self.ncols * row + col
        return self.nrows * col + row

    def get_hint(self):
        try:
            choice = self.question.choices[self.current]
            hint = self.question.hints[choice]
            if hint:
                return f"{choice}: {hint}"
            else:
                return f"{choice}"
        except (KeyError, IndexError):
            return ""

    def is_selected(self, row, col):
        if row == self.cur_row and col == self.cur_col:
            return True
        return False

    def get_option_lines(self):
        padding = " " * self.paddingsize
        for r in range(self.nrows):
            line = ""
            for c in range(self.ncols):
                i = self._index(r, c)
                if i >= len(self.options):
                    break
                option = self.options[i]
                extra = " " * (self.colwidths[c].width - option.length)

                scolor = self.theme.List.selection_color
                uscolor = self.theme.List.unselected_color
                scursor = self.theme.List.selection_cursor

                color = scolor if self.is_selected(r, c) else uscolor
                cursor = scursor if self.is_selected(r, c) else " " * len(scursor)

                line += f"{color}{cursor} {option.text}{uscolor}{extra}{padding}"
            yield line.rstrip(" ")

    def get_options(self):
        choices = self.question.choices or []
        if self.is_long:
            cmin = 0
            cmax = MAX_OPTIONS_DISPLAYED_AT_ONCE

            if half_options < self.current < len(choices) - half_options:
                cmin += self.current - half_options
                cmax += self.current - half_options
            elif self.current >= len(choices) - half_options:
                cmin += len(choices) - MAX_OPTIONS_DISPLAYED_AT_ONCE
                cmax += len(choices)

            cchoices = choices[cmin:cmax]
        else:
            cchoices = choices

        ending_milestone = max(len(choices) - half_options, half_options + 1)
        is_in_beginning = self.current <= half_options
        is_in_middle = half_options < self.current < ending_milestone
        is_in_end = self.current >= ending_milestone

        for index, choice in enumerate(cchoices):
            end_index = ending_milestone + index - half_options - 1
            if (
                (is_in_middle and index == half_options)
                or (is_in_beginning and index == self.current)
                or (is_in_end and end_index == self.current)
            ):
                color = self.theme.List.selection_color
                symbol = "+" if choice == GLOBAL_OTHER_CHOICE else self.theme.List.selection_cursor
            else:
                color = self.theme.List.unselected_color
                symbol = " " if choice == GLOBAL_OTHER_CHOICE else " " * len(self.theme.List.selection_cursor)
            yield choice, symbol, color

    def process_input(self, pressed):
        if pressed == key.UP:
            self.cur_row -= 1
            if self.cur_row < 0:
                self.cur_row = self.colwidths[self.cur_col].count - 1 if self.question.carousel else 0
            self.current = self._index(self.cur_row, self.cur_col)
            return

        if pressed == key.DOWN:
            self.cur_row += 1
            if self.cur_row >= self.colwidths[self.cur_col].count:
                self.cur_row = 0 if self.question.carousel else self.colwidths[self.cur_col].count - 1
            self.current = self._index(self.cur_row, self.cur_col)
            return

        if pressed == key.RIGHT:
            self.cur_col += 1
            if self.cur_col >= self.ncols:
                self.cur_col = 0 if self.question.carousel else self.ncols - 1
            count = self.colwidths[self.cur_col].count
            if self.cur_row >= count:
                self.cur_col -= 1
            self.current = self._index(self.cur_row, self.cur_col)
            return

        if pressed == key.LEFT:
            self.cur_col -= 1
            if self.cur_col < 0:
                self.cur_col = self.ncols - 1 if self.question.carousel else 0
            self.current = self._index(self.cur_row, self.cur_col)
            return

        if pressed == key.ENTER:
            value = self.question.choices[self.current]

            if value == GLOBAL_OTHER_CHOICE:
                value = self.other_input()
                if not value:
                    # Clear the print inquirer.text made, since the user didn't enter anything
                    print(self.terminal.move_up + self.terminal.clear_eol, end="")
                    return

            raise errors.EndOfInput(getattr(value, "value", value))

        if pressed == key.CTRL_C:
            raise KeyboardInterrupt()

    def _current_index(self):
        try:
            return self.question.choices.index(self.question.default)
        except ValueError:
            return 0
