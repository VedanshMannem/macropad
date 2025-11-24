import board
import bitbangio
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_displayio_ssd1306 import SSD1306

from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners.keypad import KeysScanner
from kmk.keys import KC
from kmk.modules.layers import Layers
from kmk.modules.macros import Macros, Press, Release, Tap
from kmk.modules.rgb import RGB
from kmk.modules.holdtap import HoldTap

keyboard = KMKKeyboard()

PINS = [board.A0, board.A1, board.A2, board.A3]

keyboard.matrix = KeysScanner(
    pins=PINS,
    value_when_pressed=False,
)

layers = Layers()
macros = Macros()
holdtap = HoldTap(tap_time=1500)
keyboard.modules.extend([layers, macros, holdtap])

rgb = RGB(
    pixel_pin=board.D6 if hasattr(board, "D6") else board.GP6,
    num_pixels=6,
    hue_default=0.0,
    sat_default=1.0,
    val_default=0.4,
)
keyboard.modules.append(rgb)

displayio.release_displays()
i2c = bitbangio.I2C(scl=board.MISO, sda=board.MOSI)
oled_i2c = displayio.I2CDisplay(i2c, device_address=0x3C)
display = SSD1306(oled_i2c, width=128, height=32)

root = displayio.Group()
display.show(root)

title = label.Label(terminalio.FONT, text="Macropad", x=2, y=10)
mode_label = label.Label(terminalio.FONT, text="Mode: UTIL", x=2, y=25)
root.append(title)
root.append(mode_label)

UTIL   = 0
VOLUME = 1
WASD   = 2

MODE_NAMES = ["UTIL", "VOLUME", "WASD"]

CHATGPT_MACRO = KC.MACRO(
    Press(KC.LCTRL), Press(KC.LALT), Tap(KC.G),
    Release(KC.LALT), Release(KC.LCTRL)
)

SCREENSHOT_MACRO = KC.MACRO(
    Press(KC.LGUI), Press(KC.LSHIFT), Tap(KC.S),
    Release(KC.LSHIFT), Release(KC.LGUI)
)

COPY_MACRO = KC.MACRO(
    Press(KC.LCTRL), Tap(KC.C), Release(KC.LCTRL)
)

PASTE_MACRO = KC.MACRO(
    Press(KC.LCTRL), Tap(KC.V), Release(KC.LCTRL)
)

HT_COPY_TO_VOLUME = KC.HT(COPY_MACRO, KC.TO(VOLUME))
HT_PASTE_TO_WASD  = KC.HT(PASTE_MACRO, KC.TO(WASD))
HT_MUTE_TO_UTIL   = KC.HT(KC.MUTE, KC.TO(UTIL))
HT_MPLY_TO_UTIL   = KC.HT(KC.MPLY, KC.TO(UTIL))
HT_S_TO_UTIL      = KC.HT(KC.S, KC.TO(UTIL))

keyboard.keymap = [
    [
        CHATGPT_MACRO,
        SCREENSHOT_MACRO,
        HT_COPY_TO_VOLUME,
        HT_PASTE_TO_WASD,
    ],
    [
        KC.VOLD,
        KC.VOLU,
        HT_MUTE_TO_UTIL,
        HT_MPLY_TO_UTIL,
    ],
    [
        KC.W,
        KC.A,
        HT_S_TO_UTIL,
        KC.D,
    ],
]

def update_visuals():
    active = keyboard.active_layers[0]
    mode = MODE_NAMES[active]
    mode_label.text = f"Mode: {mode}"

    if active == UTIL:
        rgb.set_hsv_fill(0.10, 1.0, 0.4)
    elif active == VOLUME:
        rgb.set_hsv_fill(0.33, 1.0, 0.4)
    elif active == WASD:
        rgb.set_hsv_fill(0.55, 1.0, 0.4)

def before_matrix_scan():
    update_visuals()

keyboard.before_matrix_scan = before_matrix_scan

if __name__ == '__main__':
    keyboard.go()
