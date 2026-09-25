Modify the camera to follow the player and keep the view within the boundaries of the level.

![[Pasted image 20260922140017.png|1000]]

```python title=camera.py hl=18,20-39,41-48
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

        self.bounds = None

    def set_limits_to_tilemap(self, tile_map):
        """Use the scaled tilemap edges as the camera's movement limits."""
        self.projection = arcade.LRBT(
            -self.camera_width / 2,
            self.camera_width / 2,
            -self.camera_height / 2,
            self.camera_height / 2,
        )

        map_left = tile_map.offset.x
        map_bottom = tile_map.offset.y
        map_right = map_left + tile_map.width * tile_map.tile_width * tile_map.scaling
        map_top = map_bottom + tile_map.height * tile_map.tile_height * tile_map.scaling

        self.bounds = arcade.LRBT(
            map_left + self.camera_width / 2,
            map_right - self.camera_width / 2,
            map_bottom + self.camera_height / 2,
            map_top - self.camera_height / 2,
        )

    def follow(self, sprite):
        """Center on a sprite and remain inside the configured limits."""
        self.position = sprite.position
        if self.bounds is not None:
            self.position = arcade.camera.grips.constrain_xy(
                self.view_data,
                self.bounds,
            )

```

```python title=10_player_camera.py hl=32,42,52
import arcade
import sys
from pathlib import Path

# Allow this tutorial file to be run directly from its subdirectory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from library import GameCamera, Level, Player
from library.settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT, GRAVITY, PLAYER_JUMP_SPEED,
)

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

        # Create the level from a Tiled tilemap
        self.level = Level()
        self.level.scene.add_sprite("Player", self.player)
        self.camera.set_limits_to_tilemap(self.level.tile_map)

        # Add physics to the game
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            walls=self.level.scene["Platforms"],
            gravity_constant=GRAVITY,
            ladders=self.level.scene["Ladders"],
        )

        self.camera.follow(self.player)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.level.scene.draw(pixelated=True)

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.player.on_update(delta_time)  # Sets the player direction and animation
        self.camera.follow(self.player)

    def on_key_press(self, key, key_modifiers):
        if key in (arcade.key.W, arcade.key.UP, arcade.key.SPACE):
            if self.physics_engine.can_jump():
                self.physics_engine.jump(PLAYER_JUMP_SPEED)
                     
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