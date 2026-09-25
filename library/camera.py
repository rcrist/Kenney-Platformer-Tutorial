import arcade
from pathlib import Path

from .settings import WINDOW_WIDTH, WINDOW_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT

BACKGROUND_ROOT = Path(__file__).resolve().parent.parent / "assets" / "backgrounds"
DEFAULT_BACKGROUND_PATH = BACKGROUND_ROOT / "green_fields.png"

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
        self.set_background(DEFAULT_BACKGROUND_PATH)

    def set_background(self, background_path):
        """Load the image drawn behind the current level."""
        self.background_texture = arcade.load_texture(background_path)

    def set_view_size(self, width, height):
        """Set the amount of the game world visible through the camera."""
        self.camera_width = width
        self.camera_height = height
        self.projection = arcade.LRBT(
            -width / 2,
            width / 2,
            -height / 2,
            height / 2,
        )

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

        camera_left = map_left + self.camera_width / 2
        camera_right = map_right - self.camera_width / 2
        if camera_left > camera_right:
            camera_left = camera_right = (map_left + map_right) / 2

        camera_bottom = map_bottom + self.camera_height / 2
        camera_top = map_top - self.camera_height / 2
        if camera_bottom > camera_top:
            camera_bottom = camera_top = (map_bottom + map_top) / 2

        self.bounds = arcade.LRBT(
            camera_left,
            camera_right,
            camera_bottom,
            camera_top,
        )

    def follow(self, sprite):
        """Center on a sprite and remain inside the configured limits."""
        self.position = sprite.position
        if self.bounds is not None:
            self.position = arcade.camera.grips.constrain_xy(
                self.view_data,
                self.bounds,
            )
