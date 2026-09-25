```python title=game.py
import arcade
import sys
from pathlib import Path

# Allow this tutorial file to be run directly from its subdirectory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from library import GameCamera, HudCamera, Player
from library.game_manager import GameManager
from library.settings import *

WINDOW_TITLE = "Kenney Platformer Tutorial"
class GameView(arcade.View):
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager

        self.background_color = arcade.color.SKY_BLUE
        self.camera = GameCamera()
        self.game_manager.configure_camera(self.camera)
        self.hud_camera = HudCamera()

        # Create a player
        self.player = Player()
        self.game_manager.restore_player_state(self.player, self.hud_camera)
        self.player.position = (CAMERA_WIDTH/2, CAMERA_HEIGHT/2)
        self.player.scale = 0.5

        self.level = self.game_manager.create_level()
        self.level.level_setup(self.player, self.camera)

        self.enemy_list = self.level.enemy_list
        self.physics_manager = self.level.physics_manager
        self.leaf_manager = self.level.leaf_manager

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.camera.draw_background()
        self.level.scene.draw(pixelated=True)
        self.player.draw_health_bar()
        for enemy in self.enemy_list:
            enemy.draw_health_bar()

        self.hud_camera.draw()

    def on_update(self, delta_time):
        self.physics_manager.update_player()
        self.player.keep_in_level(self.level.tile_map)

        if self.game_manager.check_for_player_death(self.player):
            return

        if self.level.check_for_exit(self.player):
            self.game_manager.complete_level(self.player)
            return

        self.level.collect_coins(self.player, self.hud_camera)
        self.level.collect_health(self.player)
        self.level.check_for_hazard_collision(self.player)
        if self.game_manager.check_for_player_death(self.player):
            return

        self.physics_manager.update_enemies()
        self.level.enemy_manager.check_for_enemy_collision(
            self.player,
            self.level.lock_list,
            self.physics_manager,
        )
        if self.game_manager.check_for_player_death(self.player):
            return

        for enemy in self.enemy_list:
            enemy.on_update(delta_time)

        self.level.scene.update_animation(delta_time)
        self.player.update_state(delta_time)
        self.player.on_update(delta_time)  # Sets the player direction and animation
        self.camera.follow(self.player)
        self.leaf_manager.update(delta_time, self.camera)

    def on_key_press(self, key, key_modifiers):
        if key in (arcade.key.W, arcade.key.UP, arcade.key.SPACE):
            self.physics_manager.jump()
                     
        self.player.on_key_press(key, key_modifiers)

    def on_key_release(self, key, key_modifiers):
        self.player.on_key_release(key, key_modifiers)

def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.center_window()

    game_manager = GameManager(window, GameView)
    game_manager.show_start_screen()
    arcade.run()  # Runs the Arcade game loop

if __name__ == "__main__":
    main()

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

STARTING_LEVEL_INDEX = 0


class GameManager:
    """Own the level sequence and switch between game views."""

    def __init__(self, window, game_view_factory):
        self.window = window
        self.game_view_factory = game_view_factory
        self.current_level_index = STARTING_LEVEL_INDEX
        self.player_health = 100
        self.player_coins = 0

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
        """Start a new game from level one."""
        self.current_level_index = STARTING_LEVEL_INDEX
        self.player_health = 100
        self.player_coins = 0
        self._show_current_level()

    def show_start_screen(self):
        """Show the menu displayed before the first level is loaded."""
        self.window.show_view(GameStartView(self))

    def complete_level(self, player):
        """Advance to the next level, or show Game Over after the last level."""
        self.save_player_state(player)
        if self.current_level_index < len(LEVELS) - 1:
            self.current_level_index += 1
            self._show_current_level()
        else:
            self.window.show_view(
                GameOverView(self, "You completed all four levels!")
            )

    def check_for_player_death(self, player):
        """Show Game Over when the player's health has been depleted."""
        if player.health > 0:
            return False

        self.window.show_view(GameOverView(self, "The player died."))
        return True

    def save_player_state(self, player):
        """Remember player progress before replacing the current game view."""
        self.player_health = player.health
        self.player_coins = player.coins

    def restore_player_state(self, player, hud_camera):
        """Apply saved progress to the player and HUD in a new level."""
        player.health = min(player.max_health, self.player_health)
        player.coins = self.player_coins
        hud_camera.set_score(player.coins)

    def _show_current_level(self):
        self.window.show_view(self.game_view_factory(self))


class GameStartView(arcade.View):
    """Opening screen that waits for the player to start the game."""

    BUTTON_WIDTH = 240
    BUTTON_HEIGHT = 64

    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        self.background_color = arcade.color.DARK_MIDNIGHT_BLUE

    @property
    def button_bounds(self):
        left = (WINDOW_WIDTH - self.BUTTON_WIDTH) / 2
        bottom = WINDOW_HEIGHT / 2 - 70
        return left, bottom, self.BUTTON_WIDTH, self.BUTTON_HEIGHT

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Kenney Platformer Tutorial",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 + 80,
            arcade.color.WHITE,
            42,
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
            "Start Game",
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


class GameOverView(arcade.View):
    """Final screen displayed after all levels have been completed."""

    BUTTON_WIDTH = 240
    BUTTON_HEIGHT = 64

    def __init__(self, game_manager, message):
        super().__init__()
        self.game_manager = game_manager
        self.message = message
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
            self.message,
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