import arcade
from pathlib import Path


from .audio_manager import MusicManager
from .level import Level
from .settings import WINDOW_HEIGHT, WINDOW_WIDTH


PROJECT_ROOT = Path(__file__).resolve().parent.parent

LEVELS = (
    {
        "map": PROJECT_ROOT / "assets/maps/level_01.json",
        "background": PROJECT_ROOT / "assets/backgrounds/green_fields.png",
        "camera_view": (960, 540),
        "player_scale": 0.75,
        "music": PROJECT_ROOT / "assets/kenney_assets/audio/Music Loops/Loops/Farm Frolics.ogg",
    },
    {
        "map": PROJECT_ROOT / "assets/maps/level_02.json",
        "background": PROJECT_ROOT / "assets/backgrounds/dark_caves.png",
        "camera_view": (960, 540),
        "player_scale": 0.75,
        "music": PROJECT_ROOT / "assets/kenney_assets/audio/Music Loops/Loops/Infinite Descent.ogg",
    },
    {
        "map": PROJECT_ROOT / "assets/maps/level_03.json",
        "background": PROJECT_ROOT / "assets/backgrounds/windy_forest.png",
        "camera_view": (640, 360),
        "player_scale": 0.5,
        "music": PROJECT_ROOT / "assets/kenney_assets/audio/Music Loops/Loops/Flowing Rocks.ogg",
    },
    {
        "map": PROJECT_ROOT / "assets/maps/level_04.json",
        "background": PROJECT_ROOT / "assets/backgrounds/robowser_fortress.png",
        "camera_view": (960, 540),
        "player_scale": 0.5,
        "music": PROJECT_ROOT / "assets/kenney_assets/audio/Music Loops/Loops/Mission Plausible.ogg",
    },
)

STARTING_LEVEL_INDEX = 3


class GameManager:
    """Own the level sequence and switch between game views."""

    def __init__(self, window, game_view_factory):
        self.window = window
        self.game_view_factory = game_view_factory
        self.current_level_index = STARTING_LEVEL_INDEX
        self.player_health = 100
        self.player_coins = 0
        self.music_manager = MusicManager()

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

    def configure_player(self, player):
        """Apply the current level's player scale."""
        player.scale = self.current_level["player_scale"]

    def start_game(self):
        """Start a new game from level one."""
        self.current_level_index = STARTING_LEVEL_INDEX
        self.player_health = 100
        self.player_coins = 0
        self._show_current_level()

    def show_start_screen(self):
        """Show the menu displayed before the first level is loaded."""
        self.music_manager.stop()
        self.window.show_view(GameStartView(self))

    def complete_level(self, player):
        """Advance to the next level, or show Game Over after the last level."""
        self.save_player_state(player)
        if self.current_level_index < len(LEVELS) - 1:
            self.current_level_index += 1
            self._show_current_level()
        else:
            self.music_manager.stop()
            self.window.show_view(
                GameOverView(self, "You completed all four levels!")
            )

    def check_for_player_death(self, player):
        """Show Game Over when the player's health has been depleted."""
        if player.health > 0:
            return False

        self.music_manager.stop()
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
        self.music_manager.play(self.current_level["music"])
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
