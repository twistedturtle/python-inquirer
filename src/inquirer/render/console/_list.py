from readchar import key

from inquirer import errors
from inquirer.render.console._other import GLOBAL_OTHER_CHOICE
from inquirer.render.console.base import MAX_OPTIONS_DISPLAYED_AT_ONCE
from inquirer.render.console.base import BaseConsoleRender
from inquirer.render.console.base import half_options


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




class Option:
    def __init__(self, text):
        self.text = text
        self.length = len(stripformatting(text))



from dataclasses import dataclass
from shutil import get_terminal_size  # Python >= 3.3
import re, math

DEFAULT_WIDTH = 80

def get_display_width():
    ''' Get width of terminal '''
    try:
        width = get_terminal_size().columns
    except:
        width = DEFAULT_WIDTH

    return width

@dataclass
class Layout:
    ''' A row, col combination '''
    rows: int = 0
    cols: int = 0


@dataclass
class ColWidth:
    ''' Hold values for each column '''
    width: int = 0
    count: int = 0


def get_layouts(maxcols, size, hsort=False, arrangement="horiz"): #sort="horiz"):
    ''' Figure out what layouts might work '''
    layouts = []
    prevrows = []
    for col in range(1, maxcols, 1):
        nrows = math.ceil(size / col)
        if nrows not in prevrows:
            layouts.append(Layout(nrows, col))
            prevrows.append(nrows)

    if arrangement == "horiz":
        layouts.reverse()
    elif arrangement == "grid":
        layouts.sort(key = lambda layout: abs(layout.rows - layout.cols))

    return layouts


def get_layouts_vert(maxrows, size, even=True, arrangement="vert"):
    ''' Figure out what layouts might work '''
    layouts = []
    prevcols = []
    for row in range(1, maxrows, 1):
        ncols = math.ceil(size / row)
        if ncols not in prevcols:
            layouts.append(Layout(row, ncols))
            prevcols.append(ncols)

    if arrangement == "vert":
        layouts.reverse()
    elif arrangement == "grid":
        layouts.sort(key = lambda layout: abs(layout.rows - layout.cols))

    return layouts

def stripformatting(s):
    ''' Strip any ansi escape sequences '''
    s = str(s)
    pat = re.compile(r'\x1B\[[0-9,;:]*?m')
    sub = pat.sub('', s)
    return sub


def get_colwidths(lst, prefixsize, paddingsize, hsort, arrangement, displaywidth=get_display_width()):
    ''' Get colwidths for a list of strings '''
    if (size := len(lst)) == 0:
        return

    if arrangement == "horiz" or arrangement == "grid":
        maxcols = min(40, size) + 1
        layouts = get_layouts(maxcols, size, hsort, arrangement)
    else:
        maxrows = min(MAX_OPTIONS_DISPLAYED_AT_ONCE, size) + 1
        layouts = get_layouts_vert(maxrows, size, hsort, arrangement)

    index = lambda nrows, row, col: nrows * col + row

    if hsort:
        index = lambda ncols, row, col: ncols * row + col

    for layout in layouts:
        nrows = layout.rows
        ncols = layout.cols

        colwidths = []
        icolwidths = []
        line_width = 0

        for col in range(ncols):
            colwidth = ColWidth()
            for row in range(nrows):
                if hsort:
                    i = index(ncols, row, col)
                else:
                    i = index(nrows, row, col)
                if i >= size:
                    break
                option = lst[i]

                plain = stripformatting(option.text)
                siz = len(plain)

                if siz >= colwidth.width:
                    colwidth.width = siz

                colwidth.count += 1

            colwidths.append(colwidth)
            line_width += colwidth.width

        line_width += prefixsize  * (len(colwidths)) + paddingsize * (len(colwidths) - 1)

        if line_width <= displaywidth-3:
            break

    return (nrows, ncols, colwidths)


class List2(BaseConsoleRender):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current = self._current_index()

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

        self.process_options(self.hsort)
        self.cur_row, self.cur_col = self._reverseindex(self.current)

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
