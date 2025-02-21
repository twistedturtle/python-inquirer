
# columnise

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


def get_layouts(maxcols, size, arrangement="horiz"):
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


def get_layouts_vert(maxrows, size, arrangement="vert"):
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
        layouts = get_layouts(maxcols, size, arrangement)
    else:
        maxrows = min(MAX_OPTIONS_DISPLAYED_AT_ONCE, size) + 1
        layouts = get_layouts_vert(maxrows, size, arrangement)

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
