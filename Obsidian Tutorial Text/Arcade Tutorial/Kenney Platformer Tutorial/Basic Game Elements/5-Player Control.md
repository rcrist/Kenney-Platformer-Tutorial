Let's give the player horizontal position control so the user can move the player left and right on the screen.

![[Pasted image 20260922110711.png|1000]]

```python title=5_player_control.py hl=33-34,36-37,39-40
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
        self.player_list.update(delta_time)

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

```python title=player.py hl=9-13,15-19
import arcade

from .settings import PLAYER_SPEED

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__(':resources:/images/animated_characters/male_person/malePerson_idle.png')

    def on_key_press(self, key, key_modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.change_x -= PLAYER_SPEED
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.change_x += PLAYER_SPEED

    def on_key_release(self, key, key_modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.change_x = 0
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.change_x = 0

```

```python title=settings.py hl=9-10
# Window constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Camera viewport constants
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 360

# Player constants
PLAYER_SPEED = 5

```

