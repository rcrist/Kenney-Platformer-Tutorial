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
    },
    {
        "map": PROJECT_ROOT / "assets/maps/level_02.json",
        "background": PROJECT_ROOT / "assets/backgrounds/dark_caves.png",
    },
    {
        "map": PROJECT_ROOT / "assets/maps/level_03.json",
        "background": PROJECT_ROOT / "assets/backgrounds/windy_forest.png",     
    },
    {
        "map": PROJECT_ROOT / "assets/maps/level_04.json",
        "background": PROJECT_ROOT / "assets/backgrounds/robowser_fortress.png",
    },
)

STARTING_LEVEL_INDEX = 0


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
        """Apply the current level's background to a game camera."""
        camera.set_background(self.current_level["background"])

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

```python title=game.py hl=13,27,31
import arcade
import random
import sys
from pathlib import Path

# Allow this tutorial file to be run directly from its subdirectory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from library import GameCamera, HudCamera, Player
from library.enemy_manager import EnemyManager
from library.game_manager import GameManager
from library.settings import *
from library import Grass, Reeds, Bush, Tree, Leaf

WINDOW_TITLE = "Kenney Platformer Tutorial"
MAX_LEAVES = 20

PRINCESS_IDLE_PATH = (
    "assets/kenney_assets/Toon Characters/Female person/PNG/Poses/"
    "character_femalePerson_idle.png"
)
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
        self.player.position = (CAMERA_WIDTH/2, CAMERA_HEIGHT/2)
        self.player.scale = 0.5

        # Create the level from a Tiled tilemap
        self.level = self.game_manager.create_level()
        if self.level.name == "level_03":
            self.player.scale = 0.5
        self.level.scene.add_sprite("Player", self.player)
        self.camera.set_limits_to_tilemap(self.level.tile_map)
        try:
            self.moving_platforms = self.level.scene["Moving Platforms"]
        except KeyError:
            self.moving_platforms = arcade.SpriteList()
        try:
            self.exit_list = self.level.scene["Exit"]
        except KeyError:
            self.exit_list = arcade.SpriteList()
        self.setup_exits()
        try:
            self.hazard_list = self.level.scene["Hazards"]
        except KeyError:
            self.hazard_list = arcade.SpriteList()
        try:
            self.ladder_list = self.level.scene["Ladders"]
        except KeyError:
            self.ladder_list = arcade.SpriteList()
        try:
            self.lock_list = self.level.scene["Locks"]
        except KeyError:
            self.lock_list = arcade.SpriteList()
        try:
            self.coin_list = self.level.scene["Coins"]
        except KeyError:
            self.coin_list = arcade.SpriteList()
        self.setup_moving_platforms()

        self.enemy_manager = EnemyManager()
        self.enemy_list = self.enemy_manager.load_enemies(self.level)

        self.enemy_physics_engines = [
            arcade.PhysicsEnginePlatformer(
                enemy,
                walls=self.level.scene["Platforms"],
                gravity_constant=0 if enemy.is_flying else GRAVITY,
                ladders=self.ladder_list,
            )
            for enemy in self.enemy_list
        ]

        # Add physics to the game
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            platforms=self.moving_platforms,
            walls=[self.level.scene["Platforms"], self.lock_list],
            gravity_constant=GRAVITY,
            ladders=self.ladder_list,
        )

        self.camera.follow(self.player)

        self.nature_list = self.load_nature()

        self.leaf_list = arcade.SpriteList()
        self.level.scene.add_sprite_list("Leaves", sprite_list=self.leaf_list)
        self.leaves_enabled = self.level.name in ("level_01", "level_03")
        self.next_leaf_time = random.uniform(0.1, 0.5)

        # Tiled layers are initially drawn before sprite lists added in code.
        # Move Foreground to the end so it appears in front of the player.
        if "Foreground" in self.level.scene:
            self.level.scene.move_sprite_list_after("Foreground", "Leaves")

    def load_nature(self):
        """Replace tilemap markers with the matching animated sprites."""
        nature_classes = {
            "Grass": Grass,
            "Tree": Tree,
            "Bush": Bush,
            "Reed": Reeds,
        }
        nature_list = arcade.SpriteList()
        try:
            nature_markers = self.level.scene.get_sprite_list("Nature")
        except KeyError:
            nature_markers = ()

        for marker in nature_markers:
            nature_type = marker.properties.get("Type")
            nature_class = nature_classes.get(nature_type)
            if nature_class is None:
                raise ValueError(f"Unknown nature type in tilemap: {nature_type}")

            nature = nature_class(marker.center_x, marker.center_y - 10)
            nature.scale = 0.1
            nature_list.append(nature)

        if "Nature" in self.level.scene:
            self.level.scene.remove_sprite_list_by_name("Nature")
        self.level.scene.add_sprite_list("Nature", sprite_list=nature_list)
        return nature_list

    def setup_moving_platforms(self):
        """Configure vertical movement from the platform custom properties."""
        tile_distance = self.level.tile_map.tile_height * self.level.tile_map.scaling

        for platform in self.moving_platforms:
            properties = platform.properties
            if "Top" not in properties or "Bottom" not in properties:
                continue

            platform.boundary_top = platform.top + properties["Top"] * tile_distance
            platform.boundary_bottom = platform.bottom - properties["Bottom"] * tile_distance
            platform.change_y = MOVING_PLATFORM_SPEED

    def setup_exits(self):
        """Replace princess exit markers with the stationary princess art."""
        princess_texture = None

        for exit_marker in self.exit_list:
            exit_type = str(exit_marker.properties.get("type", "")).lower()
            if exit_type not in ("princes", "princess"):
                continue

            if princess_texture is None:
                princess_texture = arcade.load_texture(PRINCESS_IDLE_PATH)
            exit_marker.texture = princess_texture
            exit_marker.change_x = 0
            exit_marker.change_y = 0

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
        self.physics_engine.update()
        self.keep_player_in_level()

        if self.check_for_exit():
            return

        self.collect_coins()
        self.check_for_hazard_collision()

        for physics_engine in self.enemy_physics_engines:
            physics_engine.update()
        self.check_for_enemy_collision()

        for enemy in self.enemy_list:
            enemy.on_update(delta_time)

        self.level.scene.update_animation(delta_time)
        self.player.update_state(delta_time)
        self.player.on_update(delta_time)  # Sets the player direction and animation
        self.camera.follow(self.player)
        if self.leaves_enabled:
            self.update_leaves(delta_time)

    def keep_player_in_level(self):
        """Keep the player's entire sprite inside the tilemap bounds."""
        tile_map = self.level.tile_map
        map_left = tile_map.offset.x
        map_bottom = tile_map.offset.y
        map_right = map_left + tile_map.width * tile_map.tile_width * tile_map.scaling
        map_top = map_bottom + tile_map.height * tile_map.tile_height * tile_map.scaling

        if self.player.left < map_left:
            self.player.left = map_left
            self.player.change_x = 0
        elif self.player.right > map_right:
            self.player.right = map_right
            self.player.change_x = 0

        if self.player.bottom < map_bottom:
            self.player.bottom = map_bottom
            self.player.change_y = 0
        elif self.player.top > map_top:
            self.player.top = map_top
            self.player.change_y = 0

    def update_leaves(self, delta_time):
        camera_x, camera_y = self.camera.position
        bottom = camera_y - CAMERA_HEIGHT / 2

        for leaf in tuple(self.leaf_list):
            leaf.on_update(delta_time)
            if leaf.top < bottom:
                leaf.remove_from_sprite_lists()

        self.next_leaf_time -= delta_time
        if self.next_leaf_time <= 0:
            self.next_leaf_time = random.uniform(0.1, 0.5)

            if len(self.leaf_list) < MAX_LEAVES:
                left = camera_x - CAMERA_WIDTH / 2
                top = camera_y + CAMERA_HEIGHT / 2
                leaf = Leaf(
                    random.uniform(left, left + CAMERA_WIDTH),
                    top + 8,
                )
                self.leaf_list.append(leaf)

    def collect_coins(self):
        coins_hit = arcade.check_for_collision_with_list(
            self.player,
            self.coin_list,
        )

        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            self.player.coins += 1
            self.hud_camera.set_score(self.player.coins)

    def check_for_exit(self):
        """Advance when the player reaches an Exit marker."""
        exits_hit = arcade.check_for_collision_with_list(
            self.player,
            self.exit_list,
        )

        exit_types = {"exit", "princes", "princess"}
        if any(
            str(exit_marker.properties.get("type", "")).lower() in exit_types
            for exit_marker in exits_hit
        ):
            self.game_manager.complete_level()
            return True

        return False

    def check_for_hazard_collision(self):
        """Apply the damage value stored on any hazard the player touches."""
        hazards_hit = arcade.check_for_collision_with_list(
            self.player,
            self.hazard_list,
        )

        for hazard in hazards_hit:
            damage = hazard.properties.get("Value")
            if damage is not None:
                self.player.take_damage(damage)

    def check_for_enemy_collision(self):
        enemies_hit = arcade.check_for_collision_with_list(
            self.player,
            self.enemy_list,
        )

        if enemies_hit:
            self.player.take_damage(10)
            for enemy in enemies_hit:
                enemy.take_damage(25)
                if enemy.health <= 0:
                    if enemy.enemy_type == "robobowser":
                        self.lock_list.clear()
                    enemy.remove_from_sprite_lists()

            self.enemy_physics_engines = [
                physics_engine
                for physics_engine in self.enemy_physics_engines
                if physics_engine.player_sprite.health > 0
            ]

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

    game_manager = GameManager(window, GameView)
    game_manager.start_game()
    arcade.run()  # Runs the Arcade game loop

if __name__ == "__main__":
    main()

```