# -*- coding: utf-8 -*-

# MIT License
#
# Copyright © 2016 Igor Kroitor
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 
# https://github.com/kroitor/asciichart

from math import cos
# from math import sin
from math import pi
from math import floor
from math import ceil


def plot(series, cfg={}):

    minimum = min(series)
    maximum = max(series)

    interval = abs(float(maximum) - float(minimum))
    offset = cfg['offset'] if 'offset' in cfg else 3
    # padding = cfg['padding'] if 'padding' in cfg else '       '
    height = cfg['height'] if 'height' in cfg else interval
    ratio = height / interval
    # print(minimum,ratio,type(minimum))
    min2 = floor(float(minimum) * ratio)
    max2 = ceil(float(maximum) * ratio)

    intmin2 = int(min2)
    intmax2 = int(max2)

    rows = abs(intmax2 - intmin2)
    width = len(series) + offset
    # format = cfg['format'] if 'format' in cfg else lambda x: (padding + '{:.2f}'.format(x))[:-len(padding)]

    result = [[' '] * width for i in range(rows + 1)]

    # axis and labels
    for y in range(intmin2, intmax2 + 1):
        label = '{:8.2f}'.format(float(maximum) - ((y - intmin2) * interval / rows))
        result[y - intmin2][max(offset - len(label), 0)] = label
        result[y - intmin2][offset - 1] = '┼' if y == 0 else '┤'

    y0 = int(series[0] * ratio - min2)
    result[rows - y0][offset - 1] = '┼'  # first value

    for x in range(0, len(series) - 1):  # plot the line
        y0 = int(round(series[x + 0] * ratio) - intmin2)
        y1 = int(round(series[x + 1] * ratio) - intmin2)
        if y0 == y1:
            result[rows - y0][x + offset] = '─'
        else:
            result[rows - y1][x + offset] = '╰' if y0 > y1 else '╭'
            result[rows - y0][x + offset] = '╮' if y0 > y1 else '╯'
            start = min(y0, y1) + 1
            end = max(y0, y1)
            for y in range(start, end):
                result[rows - y][x + offset] = '│'

    return '\n'.join([''.join(row) for row in result])


if __name__ == '__main__':
    width = 180
    series = [15 * cos(i * ((pi * 4) / width)) for i in range(width)]
    print(plot(series))