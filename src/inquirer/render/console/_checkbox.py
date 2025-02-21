from readchar import key

from inquirer import errors
from inquirer.render.console._other import GLOBAL_OTHER_CHOICE
from inquirer.render.console.base import MAX_OPTIONS_DISPLAYED_AT_ONCE
from inquirer.render.console.base import BaseConsoleRender
from inquirer.render.console.base import half_options

from inquirer.render.console._columnise import ColWidth, get_layouts, get_layouts_vert, stripformatting, get_colwidths, Option


class Checkbox(BaseConsoleRender):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.locked = self.question.locked or []
        self.selection = [k for (k, v) in enumerate(self.question.choices) if v in self.default_choices()]
        self.current = 0

    def get_hint(self):
        try:
            hint = self.question.hints[self.question.choices[self.current]]
            return hint or ""
        except KeyError:
            return ""

    def default_choices(self):
        default = self.question.default or []
        return default + self.locked

    @property
    def is_long(self):
        choices = self.question.choices or []
        return len(choices) >= MAX_OPTIONS_DISPLAYED_AT_ONCE

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
            if (
                (is_in_middle and self.current - half_options + index in self.selection)
                or (is_in_beginning and index in self.selection)
                or (is_in_end and index + max(len(choices) - MAX_OPTIONS_DISPLAYED_AT_ONCE, 0) in self.selection)
            ):  # noqa
                symbol = self.theme.Checkbox.selected_icon
                color = self.theme.Checkbox.selected_color
            else:
                symbol = self.theme.Checkbox.unselected_icon
                color = self.theme.Checkbox.unselected_color

            selector = " "
            end_index = ending_milestone + index - half_options - 1
            if (
                (is_in_middle and index == half_options)
                or (is_in_beginning and index == self.current)
                or (is_in_end and end_index == self.current)
            ):
                selector = self.theme.Checkbox.selection_icon
                color = self.theme.Checkbox.selection_color

            if choice in self.locked:
                color = self.theme.Checkbox.locked_option_color

            if choice == GLOBAL_OTHER_CHOICE:
                symbol = "+"

            yield choice, selector + " " + symbol, color

    def process_input(self, pressed):
        question = self.question
        is_current_choice_locked = question.choices[self.current] in self.locked
        if pressed == key.UP:
            if question.carousel and self.current == 0:
                self.current = len(question.choices) - 1
            else:
                self.current = max(0, self.current - 1)
            return
        elif pressed == key.DOWN:
            if question.carousel and self.current == len(question.choices) - 1:
                self.current = 0
            else:
                self.current = min(len(self.question.choices) - 1, self.current + 1)
            return
        elif pressed == key.SPACE:
            if self.question.choices[self.current] == GLOBAL_OTHER_CHOICE:
                self.other_input()
            elif self.current in self.selection:
                if not is_current_choice_locked:
                    self.selection.remove(self.current)
            else:
                self.selection.append(self.current)
        elif pressed == key.LEFT:
            if self.current in self.selection:
                if not is_current_choice_locked:
                    self.selection.remove(self.current)
        elif pressed == key.RIGHT:
            if self.current not in self.selection:
                self.selection.append(self.current)
        elif pressed == key.CTRL_A:
            self.selection = [i for i in range(len(self.question.choices))]
        elif pressed == key.CTRL_R:
            self.selection = []
        elif pressed == key.CTRL_I:
            self.selection = [i for i in range(len(self.question.choices)) if i not in self.selection]
        elif pressed == key.ENTER:
            result = []
            for x in self.selection:
                value = self.question.choices[x]
                result.append(getattr(value, "value", value))
            raise errors.EndOfInput(result)
        elif pressed == key.CTRL_C:
            raise KeyboardInterrupt()

    def other_input(self):
        other = super().other_input()

        # Clear the print that inquirer.text made
        print(self.terminal.move_up + self.terminal.clear_eol, end="")

        if not other:
            return

        index = self.question.add_choice(other)
        if index not in self.selection:
            self.selection.append(index)





class Checkbox2(BaseConsoleRender):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.locked = self.question.locked or []
        self.selection = [k for (k, v) in enumerate(self.question.choices) if v in self.default_choices()]
        self.current = 0


        if self.question.hsort:
            self.hsort = self.question.hsort
        elif self.theme.options.hsort:
            self.hsort = self.theme.options.hsort
        else:
            # shouldn't get here
            self.hsort = False

        # also check it's valid
        if self.question.arrangement:
            self.arrangement = self.question.arrangement
        elif self.theme.options.arrangement:
            self.arrangement = self.theme.options.arrangement
        else:
            self.arrangement = "vert"  # ["vert", "horiz", "grid"]

        if self.question.pad_size:
            self.paddingsize = self.question.pad_size
        elif self.theme.options.pad_size:
            self.paddingsize = self.theme.options.pad_size
        else:
            self.paddingsize = 2

        self.process_options()
        self.cur_row, self.cur_col = self._reverseindex(self.current)

    def get_hint(self):
        try:
            hint = self.question.hints[self.question.choices[self.current]]
            return hint or ""
        except KeyError:
            return ""

    def default_choices(self):
        default = self.question.default or []
        return default + self.locked

    @property
    def is_long(self):
        choices = self.question.choices or []
        return len(choices) >= MAX_OPTIONS_DISPLAYED_AT_ONCE

    def process_options(self, hsort=False):
        self.options = [ Option(x) for x in self.question.choices ]

        prefix_size = len(self.theme.List.selection_cursor) + 1

        self.nrows, self.ncols, self.colwidths = get_colwidths(self.options, prefix_size, self.paddingsize, hsort=self.hsort, arrangement=self.arrangement) #, displaywidth)

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

    def is_selected(self, row, col):
        if row == self.cur_row and col == self.cur_col:
            return True
        return False

    def get_option_lines(self):
        padding = " " * 2
        for r in range(self.nrows):
            line = ""
            for c in range(self.ncols):
                i = self._index(r, c)
                if i >= len(self.options):
                    break
                option = self.options[i]
                extra = " " * (self.colwidths[c].width - option.length)

                scolor  = self.theme.List.selection_color
                uscolor = self.theme.List.unselected_color
                scursor = self.theme.List.selection_cursor

                color  = scolor  if self.is_selected(r, c) else uscolor
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
            if (
                (is_in_middle and self.current - half_options + index in self.selection)
                or (is_in_beginning and index in self.selection)
                or (is_in_end and index + max(len(choices) - MAX_OPTIONS_DISPLAYED_AT_ONCE, 0) in self.selection)
            ):  # noqa
                symbol = self.theme.Checkbox.selected_icon
                color = self.theme.Checkbox.selected_color
            else:
                symbol = self.theme.Checkbox.unselected_icon
                color = self.theme.Checkbox.unselected_color

            selector = " "
            end_index = ending_milestone + index - half_options - 1
            if (
                (is_in_middle and index == half_options)
                or (is_in_beginning and index == self.current)
                or (is_in_end and end_index == self.current)
            ):
                selector = self.theme.Checkbox.selection_icon
                color = self.theme.Checkbox.selection_color

            if choice in self.locked:
                color = self.theme.Checkbox.locked_option_color

            if choice == GLOBAL_OTHER_CHOICE:
                symbol = "+"

            yield choice, selector + " " + symbol, color

    # def process_input(self, pressed):
    #     question = self.question
    #     is_current_choice_locked = question.choices[self.current] in self.locked
    #     if pressed == key.UP:
    #         if question.carousel and self.current == 0:
    #             self.current = len(question.choices) - 1
    #         else:
    #             self.current = max(0, self.current - 1)
    #         return
    #     elif pressed == key.DOWN:
    #         if question.carousel and self.current == len(question.choices) - 1:
    #             self.current = 0
    #         else:
    #             self.current = min(len(self.question.choices) - 1, self.current + 1)
    #         return
    #     elif pressed == key.SPACE:
    #         if self.question.choices[self.current] == GLOBAL_OTHER_CHOICE:
    #             self.other_input()
    #         elif self.current in self.selection:
    #             if not is_current_choice_locked:
    #                 self.selection.remove(self.current)
    #         else:
    #             self.selection.append(self.current)
    #     elif pressed == key.LEFT:
    #         if self.current in self.selection:
    #             if not is_current_choice_locked:
    #                 self.selection.remove(self.current)
    #     elif pressed == key.RIGHT:
    #         if self.current not in self.selection:
    #             self.selection.append(self.current)
    #     elif pressed == key.CTRL_A:
    #         self.selection = [i for i in range(len(self.question.choices))]
    #     elif pressed == key.CTRL_R:
    #         self.selection = []
    #     elif pressed == key.CTRL_I:
    #         self.selection = [i for i in range(len(self.question.choices)) if i not in self.selection]
    #     elif pressed == key.ENTER:
    #         result = []
    #         for x in self.selection:
    #             value = self.question.choices[x]
    #             result.append(getattr(value, "value", value))
    #         raise errors.EndOfInput(result)
    #     elif pressed == key.CTRL_C:
    #         raise KeyboardInterrupt()


    def process_input(self, pressed):
        question = self.question
        is_current_choice_locked = question.choices[self.current] in self.locked
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
                self.cur_col = 0 if self.question.carousel else self.ncols -1
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

        elif pressed == key.SPACE:
            if self.question.choices[self.current] == GLOBAL_OTHER_CHOICE:
                self.other_input()
            elif self.current in self.selection:
                if not is_current_choice_locked:
                    self.selection.remove(self.current)
            else:
                self.selection.append(self.current)

        elif pressed == key.CTRL_A:
            self.selection = [i for i in range(len(self.question.choices))]
        elif pressed == key.CTRL_R:
            self.selection = []
        elif pressed == key.CTRL_I:
            self.selection = [i for i in range(len(self.question.choices)) if i not in self.selection]

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

    def other_input(self):
        other = super().other_input()

        # Clear the print that inquirer.text made
        print(self.terminal.move_up + self.terminal.clear_eol, end="")

        if not other:
            return

        index = self.question.add_choice(other)
        if index not in self.selection:
            self.selection.append(index)
