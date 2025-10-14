# PyGamer/PyBadge Tutorial: World Exploration With Blinka

A mini-example of a world-exploring game on the PyGamer using Python. This code builds on the [bouncing balls example](https://learn.adafruit.com/circuitpython-stage-game-library/bouncing-balls). It adds: a controllable character, an explorable world larger than the screen, walls, enemies, an end goal, and a win/lose state. I learned a lot of things the hard way, so hopefully this example can help some other people. I also recommend you look over the [Adabox 12 tutorials](https://learn.adafruit.com/adabox012) if you haven't already, they have a lot of great resources for working with the PyGamer, pixel art, and basic game design.

### Tips and resources

- Remember to save off the device all the time! I've had trouble with the device corrupting if disconnected improperly from the computer, and even small jostles have disconnected it
- The hex color that renders as transparent is #FF00FF
- The Blinka sprite I use is modified from an Adafruit [sprite sheet](https://learn.adafruit.com/circuitpython-display-support-using-displayio/sprite-sheet)
- [Stage library documentation](https://circuitpython-stage.readthedocs.io/en/latest/README.html)

### New Sprite Bank

The new sprite bank has (from top to bottom):

- a black background tile
- four animation stages for Blinka (2 sets of identical images, a simple way to slow the animation speed)
- a `#` symbol for walls (I figured comments are kind of like walls for code)
- a `;` for enemies
- the python logo, as a goal location

<img src="img/sprites.png" width="32" height="512" />

### Game setup

Start with basic setup. Importing the libraries, setting the frame rate, and creating the game object should be familiar from the last tutorial. For this game, we'll also set `MOVE_SPEED` that sets how far the character moves at each step. The other new addition here is `game_state`, so we know if we're playing or have already won or lost the game.

```{python}
import ugame
import stage

MOVE_SPEED = 6 # How fast the game scrolls, values of 16+ could cause problems detecting collisions
FPS = 12 # Maximum frames per second

game_state = 'play' # State of the game: win, lose, or play

# Set up the main game display
game = stage.Stage(
    display=ugame.display, # initialized display parameter
    fps=FPS # Set maximum frame rate
)
```


### Load the image bank and set up the sprites

The first part should all be familiar from the previous tutorial. We load in our image bank, set the background, and set up our character sprite (`blinka`) to start with the first animation frame.

```{python}
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
```

Adding walls is similar, except there are a *lot* of them. The walls make a rectangle around our "world", so we can loop over a range of locations to set the top, bottom, left, and right walls. The range increases by 16 each time because each individual sprite is 16 pixels.  Many of these values are larger than the pixel width and height of our screen, and that's ok! We need to remember where they all are, but they won't show on the screen if they fall off the edge. We store all of them in the list `wall_sprites`.

```{python}
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
world_sprites = [goal_sprite] + enemy_sprites +  wall_sprites
```

The enemies and goal sprites are similar. The enemies all start off-screen and are stored in the `enemy_sprites` list, and the goal sprite is a single off-screen location. We also put all the non-character sprites into the `world_sprites` list so they're easier to update all at once later.

### Finish setting up the display

Nothing too unusual here. We add a location where we can display text if we win or lose. The text and sprites (in order from foreground to background) as well as the background object are added as layers. Then we render the game

```{python}
# Create text object to display mesages
text = stage.Text(width=12, height=11)
        
# Set the text location
text.move(x=50, y=50)

# Create a list of layers to be displayed, from foreground to background
# Background should always be last or it will cover anything behind it
game.layers = [text, blinka] + world_sprites + [background]

# Update the display
game.render_block()
```

### Start of the game loop

Like in the last tutorial, the game runs in a loop forever. If the game is in a win or lose state (i.e. not a play state), we don't want to update or allow any movement until the game is reset.

```{python}
while True:

    # If the game is over, freeze the screen until reset
    if game_state != 'play':

        game.tick()
        continue
```


### Character control

Character control is within the game loop. We use `ugame.buttons.get_pressed()` to determine if any keys are pressed and store that in the variable `keys`. We can determine which button is pressed with the attributes `ugame.K_RIGHT`, `ugame.K_LEFT`, etc. If any of the buttons are pressed, we use the `MOVE_SPEED` (which we set in the first step) to set `dx` and `dy` (the distance in pixels to move in the x and y direction, respectively).

The positive and negative values are backwards from what you might expect (negative to move right, positive to move left). This is because we don't want to actually move our Blinka sprite when the controller is pressed, we want to move the rest of the world while keeping Blinka in the middle of the screen.


```{python}
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
```

### Check for enemy collision

The `stage.collide()` method will tell you if two rectangles have a collision if you give it the top left and bottom right corner locations of the two objects. So we go through each enemy and see if our Blinka sprite's new location would collide with it. We don't use the full 16 pixel width for the enemy because a `;` is tall and narrow.


If we do hit an enemy, we change the `game_state` to lose, set the text object we created earlier to read "Game Over!", and render the block. Now each loop will be caught by the `if game.state != 'play':` condition at the beginning of the loop.

```{python}
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
```

### Check if we reached the goal

If we reach the goal, it's almost exactly the same as if we hit an enemy. Except instaed of going into a lose state, we go into the win state and display the appropriate text.

```{python}
    collision = stage.collide(ax0=blinka.x,   
                              ay0=blinka.y,  
                              ax1=blinka.x + 16,  
                              ay1=blinka.y + 16,
                              bx0=goal_sprite.x + dx,
                              by0=goal_sprite.y,
                              bx1=goal_sprite.x + dx + 16,
                              by1=goal_sprite.y + 16)

    # If Blinka reached the goal, the player wins
    if collision: 
        game_state = 'win'

        # Display the message
        text.text("You Win!")

        # Re-render block to get text to show
        game.render_block()
```

### Wall collision check

If we stoped movement control there, Blinka would be able to go through walls. This part might take a little longer to wrap your head around (it took me a lot of trial and error!) but implementing the code shouldn't be too bad.

We use the `stage.collide()` method like we did for enemies and the goal. But here we check for x and y collisions separately, because a collision in one direction doesn't prevent you from moving in the other direction. We also make Blinka's location one pixel smaller in each direction so we don't have issues with boundaries.

If there is a collision, we change the movement in that direction so Blinka stops directly next to the wall. Get the distance between the top left corners of blinka and the colliding sprite (for x: `blinka.x - sprite.x`). Then add or subtract 16 depending if we're moving right or left (to account for the full size of the sprites). If we're moving left, the world is moving to the right (positive) and the left of Blinka will collide with the right of an object. So we subtract 16 to keep the left edge of the wall from overlapping the right edge of Blinka.

```{python}
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
```

### Update sprite locations

After all that, we can finally update the sprite locations! This is very similar to the last tutorial. We update all of the sprites except Blinka, animate the Blinka sprite, render all the sprites, and then run `game.tick()`. Rendering this many sprites can cause some artifacts (I've noticed it in the wall, it doesn't always move smoothly). There are probably ways to fix that, but it works well enough for now.

```{python}
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
```
