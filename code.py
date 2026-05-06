import time
import board
import busio  # Added this import
import displayio
import framebufferio
import rgbmatrix
import adafruit_imageload
import adafruit_lis3dh

# --- Display Setup ---
displayio.release_displays()
matrix = rgbmatrix.RGBMatrix(
    width=64, height=64, bit_depth=5,
    rgb_pins=[board.MTX_R1, board.MTX_G1, board.MTX_B1, board.MTX_R2, board.MTX_G2, board.MTX_B2],
    addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD, board.MTX_ADDRE],
    clock_pin=board.MTX_CLK, latch_pin=board.MTX_LAT, output_enable_pin=board.MTX_OE,
)
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)
main_group = displayio.Group()
display.root_group = main_group

# --- I2C and Sensor Setup ---
# Use board.I2C() as a safer default, or busio.I2C(board.SCL, board.SDA)
i2c = board.I2C() 
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)
lis3dh.range = adafruit_lis3dh.RANGE_2_G

# --- Helper to Load Animations ---
def load_animation(filename):
    bitmap, palette = adafruit_imageload.load(filename,
                                             bitmap=displayio.Bitmap,
                                             palette=displayio.Palette)
    palette.make_transparent(0) 
    return bitmap, palette

# Load the sheets
dance_bmp, dance_pal = load_animation("pikadance.bmp")
walk_bmp, walk_pal = load_animation("pikawalk.bmp")
vibe_bmp, vibe_pal = load_animation("pikavibe.bmp")

# --- Animation Function ---
def play_animation(bitmap, palette, num_frames, speed, loops=1):
    temp_sprite = displayio.TileGrid(
        bitmap,
        pixel_shader=palette,
        width=1,
        height=1,
        tile_width=64,
        tile_height=64
    )
    main_group.append(temp_sprite)
    for _ in range(loops):
        for frame in range(num_frames):
            temp_sprite[0] = frame
            time.sleep(speed)
    main_group.remove(temp_sprite)

# --- Main Loop ---
while True:
    # 1. Read the accelerometer FIRST
    x, y, z = lis3dh.acceleration
    print(f"X: {x:0.2f} | Y: {y:0.2f} | Z: {z:0.2f}")

    # 2. Decide the animation based on tilt or shake
    # Logic: If tilted significantly on X or Y axis, change the dance!
    if abs(x) > 6.0:
        # Pikachu Vibes if tilted sideways
        play_animation(vibe_bmp, vibe_pal, 6, 0.1, loops=3)
    elif abs(y) > 6.0:
        # Pikachu Walks if tilted forward/back
        play_animation(walk_bmp, walk_pal, 8, 0.15, loops=2)
    else:
        # Default Dance
        play_animation(dance_bmp, dance_pal, 9, 0.1, loops=2)