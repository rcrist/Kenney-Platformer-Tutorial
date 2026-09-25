As the game development grows, we want to create a library of modules to organize our code.

Create a new folder called "library" and create 4 modules:
- `__init__.py`
- camera.py
- player.py
- settings.py

```python title=__init__.py
from .camera import GameCamera
from .player import Player
from .settings import *

```

This code makes the imports in other modules less complex.

```python title=camera.py
import arcade

from .settings import WINDOW_WIDTH, WINDOW_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT

class GameCamera(arcade.Camera2D):
    def __init__(self):
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        self.camera_width = CAMERA_WIDTH
        self.camera_height = CAMERA_HEIGHT

        super().__init__(
            viewport=arcade.LBWH(0, 0, self.window_width, self.window_height),
            projection=arcade.LBWH(0, 0, self.camera_width, self.camera_height),
            position=(0, 0),
        )

```

```python title=settings.py
# Window constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Camera viewport constants
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 360

```

```python title=player.py
import arcade

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__(':resources:/images/animated_characters/male_person/malePerson_idle.png')

```

In order to use the library, the module that imports it must know where the root directory is.

Here is an example of how to import the library from a module in a subdirectory.
```python title=4_library.py
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
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.player_list.draw(pixelated=True)

def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.center_window()

    game = GameView()
    window.show_view(game)
    arcade.run()  # Runs the Arcade game loop

if __name__ == "__main__":
    main()

```

However, Python is setup so the Main program is in the root directory of the project which simplifies the library imports.

```python title=game.py
import arcade

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

def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.center_window()

    game = GameView()
    window.show_view(game)
    arcade.run()  # Runs the Arcade game loop

if __name__ == "__main__":
    main()

```

I think this is why most Python applications have main.py in the project root directory.