import ugame
import stage

"""
Display is 160 pixels wide x 128 pixels high.
Tiles are 16x16, window is 10 tiles wide x 8 tiles high.
(0,0) is the top left of the screen.
Sprite locations are the top left point of the sprite image.
"""

MOVE_SPEED = 6 # How fast the game scrolls
FPS = 12 # Maximum frames per second

# Set up the main game display
game = stage.Stage(
    display=ugame.display, # initialized display parameter
    fps=FPS # Set maximum frame rate
)

# Load in the sprite and background images
bank = stage.Bank.from_bmp16("img/sprites.bmp")

# Set the background to tile a single 16x16 sprite from the bank
# Defaults to the first 16x16 image, but can use tile to change individual tiles
background = stage.Grid(bank, width=10, height=8)

# Create player character Blinka as a sprite
blinka = stage.Sprite(
    bank=bank, # Use the bank of images we already loaded
    frame=1, # Use the second image in the bank (0-indexed)
    x=72, # Set the x co-ordinate of the top-right corner of the sprite
    y=56, # set the y co-ordinate of the top-right corner of the sprite
)

# Set up walls as obstacles we can't pass. Each piece of wall is a sprite.
# Create sprites the same way as for blinka
wall_sprites = []
# Add left and right walls
for y in range (0, 320, 16):
    wall_sprites.append(stage.Sprite(bank, frame=5, x=0, y=y))
    wall_sprites.append(stage.Sprite(bank, frame=5, x=304, y=y))

# Add top and bottom walls
for x in range(16, 304, 16):
    wall_sprites.append(stage.Sprite(bank, frame=5, x=x, y=0))
    wall_sprites.append(stage.Sprite(bank, frame=5, x=x, y=304))

# Put all sprites that aren't Blinka in a single list. This will make things easier later
world_sprites = wall_sprites

# Create a list of layers to be displayed, from foreground to background
# Background should always be last or it will cover anything behind it
game.layers = [blinka] + world_sprites + [background]

# Update the display
game.render_block()


# Game runs in a loop forever, refreshing the screen as often as fps allows
while True:

    # If control pad/joystick buttons are pressed, determine where to move
    dx = 0 # How far to move in x direction
    dy = 0 # How far to move in y direction

    # See which buttons are pressed (if any)
    keys = ugame.buttons.get_pressed()

    # ugame.K_RIGHT will be true if the rigt button is pressed
    if keys & ugame.K_RIGHT:
        dx = -MOVE_SPEED
    elif keys & ugame.K_LEFT:
        dx = MOVE_SPEED
    if keys & ugame.K_UP:
        dy = MOVE_SPEED
    elif keys & ugame.K_DOWN:
        dy = -MOVE_SPEED

    # Update the location on all world sprites. This keeps Blinka in the center and moves the world around her.
    for sprite in world_sprites:
        # Have to call update to store old location in temp variable, otherwise it may not erase properly
        sprite.update()
        sprite.move(x=sprite.x + dx, y=sprite.y + dy)

    # Animate Blinka by changing the frame
    # Add 1 to the current frame to move on to the next one
    # The modulo (%) operator lets us wrap back to the first frame number at the end
    blinka.set_frame(frame=blinka.frame % 4 + 1)

    # Update the display of all sprites in the list
    game.render_sprites([blinka] + world_sprites)

    # Wait for the start of the next frame (limited by fps set when creating game)
    game.tick()
