import pyscreenshot
from time import sleep
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from pynput.mouse import Button, Controller
from PIL import Image
from colorsys import rgb_to_hls

# TODO: remove
SCREEN_SIZE = 466
STEP = 2

## GLOBALS
# CLI args
args = None
# currently selected colour
current_colour = (0, 0, 0)
# PIL image
image = None
# pynput mouse
mouse = None
# usable colour palette, in order of appearance from left to right
palette = []
# entire colour palette
possible_palette = []
# screen scaling
scaling = 1
# size of drawing area
screen_size = 400
# distance between swatches
swatch_dist = 40
# initial cursor position
top_left = None

def parse_args():
    """
    Parse command line arguments
    """
    parser = ArgumentParser(
        description='Automatically draw a picture for Draw Something',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-s, --step',
        dest='step',
        default=2,
        type=int,
        help='Step size between pixel checks. Higher numbers will produce better images ' \
            'at the cost of speed.'
    )
    parser.add_argument(
        '-l, -sleep',
        dest='sleep',
        default=0.01,
        type=float,
        help='Time to sleep between mouse clicks. Higher times will reduce errors.'
    )
    parser.add_argument(
        '-r, --resize',
        dest='resize',
        default=False,
        action='store_true',
        help='Resize the image to fill the drawing canvas. Will resize automatically if the ' \
            'image is larger than the screen size'
    )
    parser.add_argument(
        '-p, --palette',
        dest='get_palette',
        default=False,
        action='store_true',
        help='Get the palette that will be used and exit. Will use colour sets from convert_only ' \
            'or colour_sets if set.'
    )
    parser.add_argument(
        '-c, --colour-sets',
        dest='colour_sets',
        nargs='*',
        default=[],
        choices=['starter', 'essentials', 'holiday', 'passion', 'spring', 'exotic', 'all'],
        help='Only use the colour sets specified. Will use colours taken from the screen otherwise.'
    )
    parser.add_argument(
        '-C, --convert-only',
        dest='convert_only',
        nargs='*',
        default=[],
        choices=['starter', 'essentials', 'holiday', 'passion', 'spring', 'exotic', 'all'],
        help='Convert the image to the nearest colours available and exit. Colour sets need to be ' \
            'provided.'
    )
    parser.add_argument(
        'file',
        type=str,
        nargs='?',
        default='draw.png',
        help='Image file to draw'
    )
    return parser.parse_args()


def get_palette(colour_sets, quit=False):
    """
    Get the colour palette in use.
    If convert_only is set, use the colour sets passed in.
    """
    global args
    global possible_palette
    global screen_size
    global swatch_dist

    palette = []

    if len(colour_sets) > 0:
        if 'starter' in colour_sets or 'all' in colour_sets:
            palette.extend([
                (  0,   0,   0), # black
                (237,  27,  36), # red
                ( 43, 214,   7), # green
                (  0, 129, 230), # blue
                (250, 223,  25)  # yellow
            ])
        if 'essentials' in colour_sets or 'all' in colour_sets:
            palette.extend([
                (147, 149, 152), # grey
                (235, 220, 168), # tan
                (139,  94,  60)  # brown
            ])
        if 'holiday' in colour_sets or 'all' in colour_sets:
            palette.extend([
                (174,   0,   0), # dark red
                (  2,  88,   0), # dark green
                ( 23,  33, 108)  # dark blue
            ])
        if 'passion' in colour_sets or 'all' in colour_sets:
            palette.extend([
                (130, 255, 255), # cyan
                (252, 129, 186), # pink
                (255,  96,   0)  # orange
            ])
        if 'spring' in colour_sets or 'all' in colour_sets:
            palette.extend([
                (162, 222,  47), # light green
                (245, 175,  86), # light brown
                (179, 151,   0)  # baby puke
            ])
        if 'exotic' in colour_sets or 'all' in colour_sets:
            palette.extend([
                (255,  68, 124), # hot pink
                ( 35, 173, 148), # dark cyan
                (124,   0, 227), # purple
                ( 46, 187, 244)  # light blue
            ])
    else:
        print('Getting colours from screen')
        x, y = mouse.position
        for i in range(3):
            ss = pyscreenshot.grab(bbox=(x, y - swatch_dist / 2, x + screen_size, y))
            pixels = ss.load()
            for p in range(0, ss.size[0], 10):
                colour = pixels[p, swatch_dist / 4]
                if not any(same(colour, swatch) for swatch in possible_palette):
                    continue
                if any(same(colour, swatch) for swatch in palette):
                    continue
                palette.append(colour)
            mouse.position = from_top_left(screen_size / 2, -swatch_dist / 2)
            sleep(args.sleep)
            mouse.press(Button.left)
            sleep(args.sleep)
            mouse.move(-screen_size / 4, 0)
            sleep(args.sleep)
            mouse.release(Button.left)
            sleep(args.sleep)
        sleep(1)
        # move swatches back
        mouse.position = from_top_left(screen_size / 2, -swatch_dist / 2)
        sleep(args.sleep)
        mouse.press(Button.left)
        sleep(args.sleep)
        mouse.move(screen_size / 4, 0)
        sleep(args.sleep)
        mouse.release(Button.left)
        sleep(args.sleep)

        mouse.position = top_left

    # exit if just getting palette
    if quit:
        print(possible_palette)
        print(palette)
        exit()

    return palette


def analyse_window():
    """
    Determine the screen size of the draw something window.
    Assumes the mouse cursor is currently inside the drawing area
    """
    print('Analysing window...')
    test_step = 50

    left, top = mouse.position

    # get screen scaling
    ss = pyscreenshot.grab(bbox=(left - test_step, top, left, top + 1))
    scaling = round((ss.size[0] - 2) / test_step)

    # find left hand side of screen
    found_left = False
    while not found_left:
        ss = pyscreenshot.grab(bbox=(left - test_step, top, left, top + 1))
        pixels = ss.load()
        leftmost_colour = pixels[0, 0]
        left -= test_step
        if not same(leftmost_colour, WHITE):
            for i in range(0, test_step * scaling, scaling):
                colour = pixels[i, 0]
                if same(colour, WHITE):
                    found_left = True
                    left += i / scaling
                    break
            if not found_left:
                print('Couldn\'t find left of screen')
                exit()

    # find top of screen
    found_top = False
    while not found_top:
        ss = pyscreenshot.grab(bbox=(left, top - test_step, left + 1, top))
        pixels = ss.load()
        topmost_colour = pixels[0, 0]
        top -= test_step
        if not same(topmost_colour, WHITE):
            for i in range(0, test_step * scaling, scaling):
                colour = pixels[0, i]
                if same(colour, WHITE):
                    found_top = True
                    top += i / scaling
                    break
            if not found_top:
                print('Couldn\'t find top of screen')
                exit()

    # find right hand side of screen
    right = left
    found_right = False
    while not found_right:
        ss = pyscreenshot.grab(bbox=(right, top, right + test_step, top + 1))
        pixels = ss.load()
        rightmost_colour = pixels[test_step * scaling - 1, 0]
        right += test_step
        if not same(rightmost_colour, WHITE):
            for i in range(0, test_step * scaling, scaling):
                colour = pixels[i, 0]
                if not same(colour, WHITE):
                    found_right = True
                    # minus scaling to correct off-by-one error
                    right -= test_step + scaling
                    right += i / scaling
                    break
            if not found_right:
                print('Couldn\'t find right of screen')
                exit()

    # no need to find bottom - screen is always a square

    screen_size = right - left
    swatch_dist = screen_size * 0.127

    mouse.position = (left, top)
    return scaling, screen_size, swatch_dist, (left, top)


# available colours
BLACK = (0, 0, 0)
RED = (237, 27, 36)
GREEN = (43, 214, 7)
BLUE = (0, 129, 230)
YELLOW = (250, 223, 25)

BROWN = (139, 94, 60)
GREY = (147, 149, 152)
TAN = (235, 220, 168)
WHITE = (255, 255, 255)

ALL_COLOURS = [BLACK, BROWN, GREY, GREEN, BLUE, TAN, RED, YELLOW, WHITE]
ALL_DRAW_COLOURS = [BLACK, BROWN, GREY, GREEN, BLUE, TAN, RED, YELLOW]

def colour_diff(c1, c2):
    # get distance between two colours
    return (c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2

def closest(colour):
    # get closest usable colour to the colour
    global palette
    best = 255 * 255
    best_colour = BLACK
    pal = palette.copy()
    pal.append(WHITE)
    for c in pal:
        if colour_diff(colour, c) < best:
            best = colour_diff(colour, c)
            best_colour = c
    return best_colour

def convert_image(image):
    """
    Convert image to closest colours available in the colour set
    Also resize the image to fit the drawing area
    """
    global screen_size
    global args
    width, height = image.size
    if args.resize or width > screen_size or height > screen_size:
        ratio = screen_size / max(width, height)
        width, height = int(width * ratio), int(height * ratio)
        image = image.resize((width, height), Image.ANTIALIAS)

    pixels = image.load()
    for i in range(width):
        for j in range(height):
            pixels[i, j] = closest(pixels[i, j])
    return image

def from_top_left(x, y):
    # move a fixed amount from top left
    global top_left
    return (top_left[0] + x, top_left[1] + y)

def click():
    global args
    mouse.press(Button.left)
    sleep(args.sleep)
    mouse.release(Button.left)

def same(c1, c2):
    # compare colours
    return c1[0] == c2[0] and c1[1] == c2[1] and c1[2] == c2[2]

def select_colour(colour):
    # select a colour in the palette
    global mouse
    global current_colour
    if same(current_colour, colour):
        return
    start = mouse.position
    if same(colour, BLACK):
        print('BLACK')
        mouse.position = from_top_left(30, -30)
    if same(colour, BROWN):
        print('BROWN')
        mouse.position = from_top_left(90, -30)
    if same(colour, GREY):
        print('GREY')
        mouse.position = from_top_left(150, -30)
    if same(colour, GREEN):
        print('GREEN')
        mouse.position = from_top_left(210, -30)
    if same(colour, BLUE):
        print('BLUE')
        mouse.position = from_top_left(270, -30)
    if same(colour, TAN):
        print('TAN')
        mouse.position = from_top_left(330, -30)
    if same(colour, RED):
        print('RED')
        mouse.position = from_top_left(390, -30)
    if same(colour, YELLOW):
        print('YELLOW')
        mouse.position = from_top_left(450, -30)

    current_colour = colour
    sleep(0.1)
    click()
    sleep(0.1)
    mouse.position = start

def draw():
    global image
    global mouse
    global args
    global palette
    pixels = image.load()
    start = (mouse.position[0], mouse.position[1])
    done = {}
    w = image.size[0]
    h = image.size[1]
    print(w, h)

    i = 0
    j = 0

    # draw line by line
    for draw_colour in palette:
        print('Using colour', draw_colour)
        while j < h:
            while i < w:
                c = pixels[i, j]
                if same(c, draw_colour):
                    select_colour(c)
                    mouse.position = (start[0] + i, start[1] + j)
                    sleep(args.sleep)
                    mouse.press(Button.left)
                    sleep(args.sleep)
                    while i + 1 < w and same(pixels[i + 1, j], c):
                        i += args.step
                    mouse.position = (start[0] + i, start[1] + j)
                    mouse.release(Button.left)
                i += args.step
            j += args.step
            i = 0
        j = 0

if __name__ == '__main__':
    args = parse_args()
    mouse = Controller()
    mouse.click(Button.left)
    if len(args.convert_only) == 0:
        scaling, screen_size, swatch_dist, top_left = analyse_window()
    possible_palette = get_palette(['all'])
    sets = args.convert_only.copy()
    sets.extend(args.colour_sets)
    palette = get_palette(args.convert_only, args.get_palette)

    print('Using {0} colours: {1}'.format(len(palette), palette))
    image = convert_image(Image.open(args.file))
    image.save('converted-' + args.file)
    if len(args.convert_only) > 0:
        exit()

    draw()