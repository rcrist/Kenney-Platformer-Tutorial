We will use a built-in resource for a Tiled level map at `:resources:/tiled_maps/map_with_ladders.json`.

Opening the map in Tiled we can get the map properties, tileset properties, and layers.

![[Pasted image 20260922131423.png]]

Map Size: 20x17 tiles
Tile Size: 128x128 px

Tilesets:
- dirt
- grass
- items
- `more_tiles`

Layers
- Background - Tile Layer
- Coins - Tile Layer
- Ladders - Tile Layer
- Player Death Zones - Object Layer
- Enemies - Object Layer
- Moving Platforms - Object Layer
- Platforms - Tile Layer

Animated sprites:
- Flag
- Torch

Lets create a Level class that models this level. Note that this means we will need a Level Manager that allows us to navigate between levels in the future.

## How do we load a level?
---
Arcade is built to use tilemaps from the Tiled level editor and includes convenient load tilemap functions. Note that we will create a scene from the Tiled tilemap and add the player to the scene. The scene acts like a spritelist for all sprites in the scene.

![[Pasted image 20260922133753.png|1000]]

```python title=level.py
import arcade

class Level:
    def __init__(self):
        # Optional layer-specific settings (e.g., spatial hashing for collisions)
        layer_options = {
            "Platforms": {"use_spatial_hash": True},
        }

        # Load the JSON map file exported from the Tiled map editor
        self.tile_map = arcade.load_tilemap(
            ":resources:/tiled_maps/map_with_ladders.json",
            scaling=0.5,
            layer_options=layer_options,
        )
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

```

```python title=8_level_class.py hl=10,27-28,36
import arcade
import sys
from pathlib import Path

# Allow this tutorial file to be run directly from its subdirectory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from library import GameCamera, Level, Player
from library.settings import WINDOW_WIDTH, WINDOW_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT

WINDOW_TITLE = "Kenney Platformer Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.SKY_BLUE
        self.camera = GameCamera()

        # Create a player
        self.player = Player()
        self.player.position = (CAMERA_WIDTH/2, CAMERA_HEIGHT/2)
        self.player.scale = 0.5

        self.level = Level()
        self.level.scene.add_sprite("Player", self.player)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.level.scene.draw(pixelated=True)

    def on_update(self, delta_time):
        self.level.scene.update(delta_time)  # Sets the player velocity
        self.player.on_update(delta_time)  # Sets the player direction and animation

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