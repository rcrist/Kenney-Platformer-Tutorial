import arcade
from arcade.future.light import Light, LightLayer

from .settings import WINDOW_HEIGHT, WINDOW_WIDTH


DARK_LEVELS = {"level_02", "level_04"}
AMBIENT_LIGHT = (18, 20, 28)
PLAYER_LIGHT_RADIUS = 180
PLAYER_LIGHT_COLOR = (255, 244, 214)


class LightingManager:
    """Darken selected levels and keep a soft light centered on the player."""

    def __init__(self, level_name, player):
        self.player = player
        self.enabled = level_name in DARK_LEVELS
        self.light_layer = None
        self.player_light = None

        if self.enabled:
            self.light_layer = LightLayer(WINDOW_WIDTH, WINDOW_HEIGHT)
            self.light_layer.set_background_color(arcade.color.BLACK)
            self.player_light = Light(
                player.center_x,
                player.center_y,
                radius=PLAYER_LIGHT_RADIUS,
                color=PLAYER_LIGHT_COLOR,
                mode="soft",
            )
            self.light_layer.add(self.player_light)

    def update(self):
        if self.enabled:
            self.player_light.position = self.player.position

    def draw(self, draw_world):
        """Draw the world normally or through the configured light layer."""
        if not self.enabled:
            draw_world()
            return

        with self.light_layer:
            draw_world()
        self.light_layer.draw(ambient_color=AMBIENT_LIGHT)
