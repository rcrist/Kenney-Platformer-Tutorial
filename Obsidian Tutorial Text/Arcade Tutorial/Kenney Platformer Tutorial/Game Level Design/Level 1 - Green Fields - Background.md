Here are the concept drawings for the 4 game levels.

![[Pasted image 20260922150454.png|1400]]

Looking at Level 1 - Green Fields it shows overlapping grass covered platforms, water, bridge, enemies, Mario style floating blocks, vegetation and a castle/mountains background image.

Lets ask AI to give us a background image that we can apply to the camera.

![[green_fields.png|1000]]

That is not bad. Image size: 1672 x 941. Lets add it as the background image to the game camera so it is always behind the platforms, players, and enemies.

![[Pasted image 20260924073644.png|1000]]

Wow! The background image makes our game seem real.

```python title=camera.py hl=2,6,22,24-34
import arcade
from pathlib import Path

from .settings import WINDOW_WIDTH, WINDOW_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT

BACKGROUND_PATH = Path(__file__).resolve().parent.parent / "assets" / "backgrounds" / "green_fields.png"

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
        self.background_texture = arcade.load_texture(BACKGROUND_PATH)

    def draw_background(self):
        """Draw the background so it always fills the game camera."""
        arcade.draw_texture_rect(
            self.background_texture,
            arcade.XYWH(
                self.position.x,
                self.position.y,
                self.camera_width,
                self.camera_height,
            ),
        )

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

```python title=game.py hl=6
...

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.camera.draw_background()
        self.level.scene.draw(pixelated=True)
        self.player.draw_health_bar()
        for enemy in self.enemy_list:
            enemy.draw_health_bar()

        self.hud_camera.draw()

...
```

