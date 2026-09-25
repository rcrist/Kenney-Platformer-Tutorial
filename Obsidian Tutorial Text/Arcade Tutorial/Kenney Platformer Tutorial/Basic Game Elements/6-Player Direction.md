Currently, the player is facing to the right even when he is moving left. In Arcade, it is recommended that we create a set of sprites for each direction.

![[Pasted image 20260922112931.png|1000]]

```python title=player.py hl=2,6-8,13-17,19,21,23-31,36,39
import arcade
from enum import Enum, auto

from .settings import PLAYER_SPEED

class Dir(Enum):
    RIGHT = 0
    LEFT = 1

class Player(arcade.Sprite):
    def __init__(self):
        # Create idle sprites facing left and right
        idle_right_texture = arcade.load_texture(
            ':resources:/images/animated_characters/male_person/malePerson_idle.png'
        )
        idle_left_texture = idle_right_texture.flip_left_right()
        self.idle_textures = [idle_right_texture, idle_left_texture] # Index 0 = right, index 1 = left

        super().__init__(idle_right_texture)

        self.current_direction = Dir.RIGHT

    def on_update(self, delta_time):
        # Set the player direction
        match self.current_direction:
            case Dir.LEFT:
                self.texture = self.idle_textures[1]
            case Dir.RIGHT:
                self.texture = self.idle_textures[0]
            case _:
                self.texture = self.idle_textures[0]


    def on_key_press(self, key, key_modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.current_direction = Dir.LEFT
            self.change_x -= PLAYER_SPEED
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.current_direction = Dir.RIGHT
            self.change_x += PLAYER_SPEED

    def on_key_release(self, key, key_modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.change_x = 0
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.change_x = 0

```

```python title=6_player_direction.py hl=35
import arcade
import sys
from pathlib import Path

# Allow this tutorial file to be run directly from its subdirectory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from library import Player, GameCamera
from library.settings import WINDOW_WIDTH, WINDOW_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT

WINDOW_TITLE = "Kenney Platformer Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.SKY_BLUE
        self.camera = GameCamera()

        self.player = Player()
        self.player.position = (CAMERA_WIDTH/2, CAMERA_HEIGHT/2)
        self.player.scale = 0.5
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.player_list.draw(pixelated=True)

    def on_update(self, delta_time):
        self.player_list.update(delta_time)  # Sets the player velocity
        self.player.on_update(delta_time) # Sets the player direction and animation

    def on_key_press(self, key, key_modifiers):
        self.player.on_key_press(key, key_modifiers)

    def on_key_release(self, key, key_modifiers):
        self.player.on_key_release(key, key_modifiers)

def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.center_window()

    game = GameView()
    window.show_view(game)
    arcade.run()  # Runs the Arcade game loop

if __name__ == "__main__":
    main()

```