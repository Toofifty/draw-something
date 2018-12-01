# Draw Something Automatically

Draws any image for the Draw Something game, (desktop only)

![Draw Something 16x](draw-something-16x.gif)

(sped up 16x)

Requires Python 3, PIL, pynput and pyscreenshot (available via pip):

`pip3 install pillow pynput pyscreenshot`

## Usage

Open Draw Something via Messenger ([Caprine](https://sindresorhus.com/caprine/) is a good choice)

Copy the image to the root of the repository. By default the script will look for `draw.png` but any image file can be specified in the command.

Make sure black, smallest width is selected and the colours are scrolled all the way to the left.

Hover over the drawing area, then run `python3 draw.py`. Use `python3 draw.py -h` for more options.