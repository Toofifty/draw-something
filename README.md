# Draw Something Automatically

Draws any image for the Draw Something game, on desktop only

![Draw Something 16x](draw-something-16x.gif)

(sped up 16x)

Requires Python 3, PIL and pynput (available via pip)

## Usage

Open Draw Something via Messenger ([Caprine](https://sindresorhus.com/caprine/) is a good choice)

Copy the image to `draw.png` in the root of the repository. It needs to be smaller than the drawing area (466x466). This might be different for different OS scaling levels so YMMV.

Make sure black, smallest width is selected and the colours are scrolled all the way to the left.

Run `python3 draw.py` in terminal to start, move your cursor over the very top left of the drawing area, and press enter.