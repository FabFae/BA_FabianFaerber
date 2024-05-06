import time
import board
import neopixel
num_leds = 90

pixels = neopixel.NeoPixel(board.D18, num_leds, brightness=1, auto_write=True)
leds_used = 69


for led in range(leds_used*3):

    pixels.fill((0, 0, 0))
    pixels[led%leds_used] = (255, 255, 255)
    pixels[(led-1)%leds_used] = (255, 255, 255)
    time.sleep(.003)
    print(led%leds_used)


pixels.fill((0, 0, 0))
print("------> done")
    


