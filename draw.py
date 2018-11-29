import time
from pynput.mouse import Button, Controller
from PIL import Image

SCREEN_SIZE = 466
STEP = 2

# available colours
BLACK = (0, 0, 0)
BROWN = (139, 94, 60)
GREY = (147, 149, 152)
GREEN = (43, 214, 7)
BLUE = (0, 129, 230)
TAN = (235, 220, 168)
RED = (237, 27, 36)
YELLOW = (250, 223, 25)
WHITE = (255, 255, 255)

ALL_COLOURS = [BLACK, BROWN, GREY, GREEN, BLUE, TAN, RED, YELLOW, WHITE]
ALL_DRAW_COLOURS = [BLACK, BROWN, GREY, GREEN, BLUE, TAN, RED, YELLOW]

mouse = None
top_left = None
current_colour = BLACK
image = None

def colour_diff(c1, c2):
    # get distance between two colours
    return (c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2

def closest(colour):
    # get closest usable colour to the colour
    best = 255 * 255
    best_colour = BLACK
    for c in ALL_COLOURS:
        if colour_diff(colour, c) < best:
            best = colour_diff(colour, c)
            best_colour = c
    return best_colour

def get_closest_colours(image):
    # change all colours to the closest in ALL_COLOURS
    pixels = image.load()
    for j in range(image.size[0]):
        for i in range(image.size[1]):
            pixels[j, i] = closest(pixels[j, i])
    return image

def from_top_left(x, y):
    # move a fixed amount from top left
    global top_left
    return (top_left[0] + x, top_left[1] + y)

def click():
    mouse.press(Button.left)
    time.sleep(0.01)
    mouse.release(Button.left)

def is_colour(c1, c2):
    # compare colours
    return c1[0] == c2[0] and c1[1] == c2[1] and c1[2] == c2[2]

def select_colour(colour):
    # select a colour in the palette
    global mouse
    global current_colour
    if is_colour(current_colour, colour):
        return
    start = mouse.position
    if is_colour(colour, BLACK):
        print('BLACK')
        mouse.position = from_top_left(30, -30)
    if is_colour(colour, BROWN):
        print('BROWN')
        mouse.position = from_top_left(90, -30)
    if is_colour(colour, GREY):
        print('GREY')
        mouse.position = from_top_left(150, -30)
    if is_colour(colour, GREEN):
        print('GREEN')
        mouse.position = from_top_left(210, -30)
    if is_colour(colour, BLUE):
        print('BLUE')
        mouse.position = from_top_left(270, -30)
    if is_colour(colour, TAN):
        print('TAN')
        mouse.position = from_top_left(330, -30)
    if is_colour(colour, RED):
        print('RED')
        mouse.position = from_top_left(390, -30)
    if is_colour(colour, YELLOW):
        print('YELLOW')
        mouse.position = from_top_left(450, -30)

    current_colour = colour
    time.sleep(0.1)
    click()
    time.sleep(0.1)
    mouse.position = start

def draw():
    global image
    global mouse
    pixels = image.load()
    start = (mouse.position[0], mouse.position[1])
    done = {}
    w = image.size[0]
    h = image.size[1]
    print(w, h)

    i = 0
    j = 0

    # draw line by line
    for draw_colour in ALL_DRAW_COLOURS:
        while j < h:
            while i < w:
                c = pixels[i, j]
                print(i, j, c, draw_colour)
                if is_colour(c, draw_colour):
                    select_colour(c)
                    mouse.position = (start[0] + i, start[1] + j)
                    time.sleep(0.01)
                    mouse.press(Button.left)
                    time.sleep(0.01)
                    while i + 1 < w and is_colour(pixels[i + 1, j], c):
                        i += STEP
                    mouse.position = (start[0] + i, start[1] + j)
                    mouse.release(Button.left)
                i += STEP
            j += STEP
            i = 0
        j = 0

def main():
    global top_left
    global mouse
    global image
    im = Image.open('draw.png')
    pixels = im.load()

    if im.size[0] > SCREEN_SIZE or im.size[1] > SCREEN_SIZE:
        print('Image too big, max = {0}x{0} (is {1}x{2})'.format(SCREEN_SIZE, im.size[0], im.size[1]))
        exit()

    image = get_closest_colours(im)
    im.save('converted.png')

    input('Move cursor to top left of drawing board, then press enter to start')

    mouse = Controller()
    top_left = mouse.position
    # select window
    click()

    # go to start of image
    mouse.position = from_top_left((SCREEN_SIZE - im.size[0]) / 2, (SCREEN_SIZE - im.size[1]) / 2)
    time.sleep(1)
    draw()

if __name__ == '__main__':
    main()