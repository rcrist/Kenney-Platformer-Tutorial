```python title=camera.py
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

```

```python title=game_manager.py
import arcade
from pathlib import Path


from .level import Level
from .settings import WINDOW_HEIGHT, WINDOW_WIDTH


PROJECT_ROOT = Path(__file__).resolve().parent.parent

LEVELS = (
    {
        "map": PROJECT_ROOT / "assets/maps/level_01.json",
        "background": PROJECT_ROOT / "assets/backgrounds/green_fields.png",
        "camera_view": (960, 540),
    },
    {
        "map": PROJECT_ROOT / "assets/maps/level_02.json",
        "background": PROJECT_ROOT / "assets/backgrounds/dark_caves.png",
        "camera_view": (960, 540),
    },
    {
        "map": PROJECT_ROOT / "assets/maps/level_03.json",
        "background": PROJECT_ROOT / "assets/backgrounds/windy_forest.png",
        "camera_view": (640, 360),
    },
    {
        "map": PROJECT_ROOT / "assets/maps/level_04.json",
        "background": PROJECT_ROOT / "assets/backgrounds/robowser_fortress.png",
        "camera_view": (960, 540),
    },
)

STARTING_LEVEL_INDEX = 3


class GameManager:
    """Own the level sequence and switch between game views."""

    def __init__(self, window, game_view_factory):
        self.window = window
        self.game_view_factory = game_view_factory
        self.current_level_index = STARTING_LEVEL_INDEX

    def create_level(self):
        """Create the level at the current position in the level sequence."""
        return Level(self.current_level["map"])

    @property
    def current_level(self):
        return LEVELS[self.current_level_index]

    def configure_camera(self, camera):
        """Apply the current level's background and view size to a camera."""
        camera.set_background(self.current_level["background"])
        camera.set_view_size(*self.current_level["camera_view"])

    def start_game(self):
        """Start a new game from the configured starting level."""
        self.current_level_index = STARTING_LEVEL_INDEX
        self._show_current_level()

    def complete_level(self):
        """Advance to the next level, or show Game Over after the last level."""
        if self.current_level_index < len(LEVELS) - 1:
            self.current_level_index += 1
            self._show_current_level()
        else:
            self.window.show_view(GameOverView(self))

    def _show_current_level(self):
        self.window.show_view(self.game_view_factory(self))


class GameOverView(arcade.View):
    """Final screen displayed after all levels have been completed."""

    BUTTON_WIDTH = 240
    BUTTON_HEIGHT = 64

    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        self.background_color = arcade.color.DARK_MIDNIGHT_BLUE

    @property
    def button_bounds(self):
        left = (WINDOW_WIDTH - self.BUTTON_WIDTH) / 2
        bottom = WINDOW_HEIGHT / 2 - 100
        return left, bottom, self.BUTTON_WIDTH, self.BUTTON_HEIGHT

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Game Over",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 + 70,
            arcade.color.WHITE,
            48,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            "You completed all four levels!",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 + 10,
            arcade.color.LIGHT_GRAY,
            20,
            anchor_x="center",
            anchor_y="center",
        )

        left, bottom, width, height = self.button_bounds
        arcade.draw_lbwh_rectangle_filled(
            left,
            bottom,
            width,
            height,
            arcade.color.DARK_BLUE_GRAY,
        )
        arcade.draw_text(
            "Restart Game",
            WINDOW_WIDTH / 2,
            bottom + height / 2,
            arcade.color.WHITE,
            22,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            "Click the button or press Enter",
            WINDOW_WIDTH / 2,
            bottom - 30,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center",
            anchor_y="center",
        )

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.ENTER, arcade.key.RETURN, arcade.key.SPACE):
            self.game_manager.start_game()

    def on_mouse_press(self, x, y, button, modifiers):
        left, bottom, width, height = self.button_bounds
        if left <= x <= left + width and bottom <= y <= bottom + height:
            self.game_manager.start_game()

```

```python title=leaf.py
import random

import arcade

from .nature import ASSET_ROOT, AnimatedNatureSprite


MAX_LEAVES = 20
LEAF_LEVELS = {"level_01", "level_03"}


class Leaf(AnimatedNatureSprite):
    texture_root = ASSET_ROOT
    texture_folder = "leaf"
    frame_count = 18
    first_frame = 0
    filename_digits = 2
    randomize_animation = True

    def __init__(self, x: float, y: float):
        self.seconds_per_frame = random.uniform(0.06, 0.16)
        super().__init__(x, y)
        self.scale = 2
        self.fall_speed = random.uniform(20, 45)
        self.drift_speed = random.uniform(-12, 12)

    def on_update(self, delta_time: float):
        self.center_x += self.drift_speed * delta_time
        self.center_y -= self.fall_speed * delta_time


class LeafManager:
    """Create, update, and remove the falling leaves for a level."""

    def __init__(self, level):
        self.enabled = level.name in LEAF_LEVELS
        self.leaf_list = arcade.SpriteList()
        self.next_leaf_time = random.uniform(0.1, 0.5)

        level.scene.add_sprite_list("Leaves", sprite_list=self.leaf_list)

        # Tiled layers are initially drawn before sprite lists added in code.
        # Keep the foreground in front of the leaves and player.
        if "Foreground" in level.scene:
            level.scene.move_sprite_list_after("Foreground", "Leaves")

    def update(self, delta_time, camera):
        if not self.enabled:
            return

        camera_x, camera_y = camera.position
        bottom = camera_y - camera.camera_height / 2

        for leaf in tuple(self.leaf_list):
            leaf.on_update(delta_time)
            if leaf.top < bottom:
                leaf.remove_from_sprite_lists()

        self.next_leaf_time -= delta_time
        if self.next_leaf_time > 0:
            return

        self.next_leaf_time = random.uniform(0.1, 0.5)
        if len(self.leaf_list) >= MAX_LEAVES:
            return

        left = camera_x - camera.camera_width / 2
        top = camera_y + camera.camera_height / 2
        leaf = Leaf(
            random.uniform(left, left + camera.camera_width),
            top + 8,
        )
        self.leaf_list.append(leaf)

```