import ugame
import stage

"""
Display is 160 pixels wide x 128 pixels high.
Tiles are 16x16, window is 10 tiles wide x 8 tiles high.
(0,0) is the top left of the screen.
Sprite locations are the top left point of the sprite image.
"""

MOVE_SPEED = 6 # How fast the game scrolls, values of 16+ could cause problems detecting collisions
FPS = 12 # Maximum frames per second

game_state = 'play' # State of the game: win, lose, or play

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

# Add enemies
enemy_sprites = [
    stage.Sprite(bank, frame=6, x=100, y=100),
    stage.Sprite(bank, frame=6, x=200, y=200),
    stage.Sprite(bank, frame=6, x=200, y=240),
    stage.Sprite(bank, frame=6, x=180, y=220)
]

# Add goal
goal_sprite = stage.Sprite(bank, frame=7, x=200, y=220)

# Put all sprites that aren't Blinka in a single list. This will make things easier later
world_sprites = [goal_sprite] + enemy_sprites +  wall_sprites

# Create text object to display mesages
text = stage.Text(width=12, height=11)
        
# Set the text location
text.move(x=50, y=50)

# Create a list of layers to be displayed, from foreground to background
# Background should always be last or it will cover anything behind it
game.layers = [text, blinka] + world_sprites + [background]

# Update the display
game.render_block()

# Game runs in a loop forever, refreshing the screen as often as fps allows
while True:

    # If the game is over, freeze the screen until reset
    if game_state != 'play':

        game.tick()
        continue

    # If control pad/joystick buttons are pressed, determine where to move
    dx = 0 # How far to move in x direction
    dy = 0 # How far to move in y direction

    # See which buttons are pressed (if any)
    keys = ugame.buttons.get_pressed()

    # ugame.K_RIGHT will be true if the right button is pressed
    if keys & ugame.K_RIGHT:
        dx = -MOVE_SPEED
    # ugame.K_LEFT will be true if the left button is pressed
    elif keys & ugame.K_LEFT:
        dx = MOVE_SPEED
    # ugame.K_UP will be true if the up button is pressed
    if keys & ugame.K_UP:
        dy = MOVE_SPEED
    # ugame.K_DOWN will be true if the down button is pressed
    elif keys & ugame.K_DOWN:
        dy = -MOVE_SPEED

    # Keep Blinka from going through walls
    for sprite in wall_sprites:
        # Check if the movement in x direction would cause a collision
        x_collision = stage.collide(ax0=blinka.x + 1,   # Make Blinka 1 pixel smaller in each direction
                                    ay0=blinka.y + 1,   # to prevent issues with collisions on the
                                    ax1=blinka.x + 15,  # boundary line
                                    ay1=blinka.y + 15,
                                    bx0=sprite.x + dx,
                                    by0=sprite.y,
                                    bx1=sprite.x + dx + 16,
                                    by1=sprite.y + 16)

        # If x movement would cause a collision, limit movement so Blinka is next to wall
        # dx/abs(dx) gets whether dx is above or below 0, determines whether we add or subtract 16
        if x_collision and dx != 0: 
            dx = blinka.x - sprite.x - dx / abs(dx) * 16
        
        # Check if the movement in y direction would cause a collision
        y_collision = stage.collide(ax0=blinka.x + 1,   # Make Blinka 1 pixel smaller in each direction
                                    ay0=blinka.y + 1,   # to prevent issues with collisions on the
                                    ax1=blinka.x + 15,  # boundary line
                                    ay1=blinka.y + 15,
                                    bx0=sprite.x,
                                    by0=sprite.y + dy,
                                    bx1=sprite.x + 16,
                                    by1=sprite.y + dy + 16)

        # If y movement would cause a collision, limit movement so Blinka is next to wall
        # dy/abs(dy) gets whether dx is above or below 0, determines whether we add or subtract 16
        if y_collision and dy != 0: 
            dy = blinka.y - sprite.y - dy / abs(dy) * 16

    # Check if Blinka hits an enemy (causes Game Over)
    for sprite in enemy_sprites:
        collision = stage.collide(ax0=blinka.x,   
                                  ay0=blinka.y,  
                                  ax1=blinka.x + 16,  
                                  ay1=blinka.y + 16,
                                  bx0=sprite.x + 4 + dx, # Enemy is narrow, move left edge 4 pixels towards middle
                                  by0=sprite.y,
                                  bx1=sprite.x + dx + 12, # Enemy is narrow, move right edge 4 pixels towards middle
                                  by1=sprite.y + 16)

        # If there is an enemy collision, the game is over
        if collision:
            game_state = 'lose'

            # Display the message
            text.text("Game Over!")

            # Re-render block to get text to show
            game.render_block()

    # Check if Blinka reached the goal (causes Win)
    collision = stage.collide(ax0=blinka.x,   
                              ay0=blinka.y,  
                              ax1=blinka.x + 16,  
                              ay1=blinka.y + 16,
                              bx0=goal_sprite.x + dx,
                              by0=goal_sprite.y,
                              bx1=goal_sprite.x + dx + 16,
                              by1=goal_sprite.y + 16)

    # If there is an enemy collision, the player wins
    if collision: 
        game_state = 'win'

        # Display the message
        text.text("You Win!")

        # Re-render block to get text to show
        game.render_block()
            

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
