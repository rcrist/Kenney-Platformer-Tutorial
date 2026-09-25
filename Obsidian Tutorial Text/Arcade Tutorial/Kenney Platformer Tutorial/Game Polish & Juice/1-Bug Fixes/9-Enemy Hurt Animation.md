-  [x] Level 1 - 4 Robots
-  [x] Level 2 - 1 Slime Block, 3 Spiders, 4 Ghosts, 3 Bats
-  [x] Level 3 - 1 Mad Block, 3 Snails, 3 Slimes, 4 Flies
-  [x] Level 4 - 5 Aliens, 5 Saucers, Robowser
-  [x] Player hurt animation

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

        self.level = self.game_manager.create_level()
        self.game_manager.configure_player(self.player)
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

```python title=level.py
import arcade
from pathlib import Path

from .enemy_manager import EnemyManager
from .leaf import LeafManager
from .nature import load_nature
from .physics import PhysicsManager
from .settings import MOVING_PLATFORM_SPEED


PRINCESS_IDLE_PATH = (
    "assets/kenney_assets/Toon Characters/Female person/PNG/Poses/"
    "character_femalePerson_idle.png"
)


class Level:
    def __init__(self, map_path="assets/maps/level_01.json"):
        # Optional layer-specific settings (e.g., spatial hashing for collisions)
        layer_options = {
            "Platforms": {"use_spatial_hash": True},
            "Locks": {"use_spatial_hash": True},
        }

        # Load the JSON map file exported from the Tiled map editor
        self.map_path = Path(map_path)
        self.name = self.map_path.stem
        self.tile_map = arcade.load_tilemap(
            # ":resources:/tiled_maps/map_with_ladders.json",
            self.map_path,
            scaling=0.5,
            layer_options=layer_options,
        )
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

    def level_setup(self, player, camera):
        """Build the runtime objects and systems associated with this level."""
        self.scene.add_sprite("Player", player)
        camera.set_limits_to_tilemap(self.tile_map)

        self.moving_platforms = self.get_layer("Moving Platforms")
        self.exit_list = self.get_layer("Exit")
        self.hazard_list = self.get_layer("Hazards")
        self.ladder_list = self.get_layer("Ladders")
        self.lock_list = self.get_layer("Locks")
        self.coin_list = self.get_layer("Coins")
        self.health_list = self.get_layer("Health")

        self.setup_exits()
        self.setup_moving_platforms()

        self.enemy_manager = EnemyManager()
        self.enemy_list = self.enemy_manager.load_enemies(self)
        self.physics_manager = PhysicsManager(
            player,
            self.enemy_list,
            moving_platforms=self.moving_platforms,
            player_walls=[self.scene["Platforms"], self.lock_list],
            enemy_walls=self.scene["Platforms"],
            ladders=self.ladder_list,
        )

        camera.follow(player)
        self.nature_list = load_nature(self)
        self.leaf_manager = LeafManager(self)

    def get_layer(self, name):
        """Return a scene layer or an empty sprite list when it is optional."""
        try:
            return self.scene[name]
        except KeyError:
            return arcade.SpriteList()

    def collect_coins(self, player, hud_camera):
        """Collect coins touched by the player and update the HUD score."""
        coins_hit = arcade.check_for_collision_with_list(player, self.coin_list)

        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            player.coins += 1
            hud_camera.set_score(player.coins)

    def collect_health(self, player):
        """Consume touched health pickups and restore up to 25 health each."""
        health_pickups = arcade.check_for_collision_with_list(
            player,
            self.health_list,
        )

        for health_pickup in health_pickups:
            health_pickup.remove_from_sprite_lists()
            player.health = min(player.max_health, player.health + 25)

    def check_for_exit(self, player):
        """Return whether the player has touched a valid exit marker."""
        exits_hit = arcade.check_for_collision_with_list(player, self.exit_list)
        exit_types = {"exit", "princes", "princess"}
        return any(
            str(exit_marker.properties.get("type", "")).lower() in exit_types
            for exit_marker in exits_hit
        )

    def check_for_hazard_collision(self, player):
        """Apply the configured damage for hazards touched by the player."""
        hazards_hit = arcade.check_for_collision_with_list(player, self.hazard_list)

        for hazard in hazards_hit:
            damage = hazard.properties.get("Value")
            if damage is not None:
                player.take_damage(damage)

    def setup_moving_platforms(self):
        """Configure vertical movement from platform custom properties."""
        tile_distance = self.tile_map.tile_height * self.tile_map.scaling

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
        "player_scale": 0.5,
    },
    {
        "map": PROJECT_ROOT / "assets/maps/level_02.json",
        "background": PROJECT_ROOT / "assets/backgrounds/dark_caves.png",
        "camera_view": (960, 540),
        "player_scale": 0.75,
    },
    {
        "map": PROJECT_ROOT / "assets/maps/level_03.json",
        "background": PROJECT_ROOT / "assets/backgrounds/windy_forest.png",
        "camera_view": (640, 360),
        "player_scale": 0.5,
    },
    {
        "map": PROJECT_ROOT / "assets/maps/level_04.json",
        "background": PROJECT_ROOT / "assets/backgrounds/robowser_fortress.png",
        "camera_view": (960, 540),
        "player_scale": 0.5,
    },
)

STARTING_LEVEL_INDEX = 1


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

```python title=enemy_manager.py
import arcade

from .enemy import Enemy
from .settings import ENEMY_SPEED

ENEMY_TEXTURES = {
    "robot1": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_blueDrive{i}.png",
    "robot2": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_greenDrive{i}.png",
    "robot3": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_redDrive{i}.png",
    "robot4": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_yellowDrive{i}.png",
}

ROBOT_DAMAGE_TEXTURES = {
    "robot1": "blue",
    "robot2": "green",
    "robot3": "red",
    "robot4": "yellow",
}
ROBOT_TEXTURE_ROOT = "assets/kenney_assets/Robot Pack/PNG/Side view"

EXTENDED_ENEMY_ROOT = "assets/kenney_assets/Platformer Art Extended Enemies/Enemy sprites"
ALIEN_ROOT = "assets/kenney_assets/Platformer Art Extended Enemies/Alien sprites"
SAUCER_ROOT = "assets/kenney_assets/Alien UFO Pack/PNG"
ROBOWSER_ROOT = "assets/kenney_assets/Toon Characters/Robot/PNG/Poses"

EXTENDED_ENEMY_ANIMATIONS = {
    "spider": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/spider.png",
        "walk": [
            f"{EXTENDED_ENEMY_ROOT}/spider_walk1.png",
            f"{EXTENDED_ENEMY_ROOT}/spider_walk2.png",
        ],
        "damage": [f"{EXTENDED_ENEMY_ROOT}/spider_hit.png"],
    },
    "slime": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/slime.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/slime_walk.png"],
        "damage": [f"{EXTENDED_ENEMY_ROOT}/slime_hit.png"],
    },
    "snail": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/snail.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/snail_walk.png"],
        "damage": [f"{EXTENDED_ENEMY_ROOT}/snail_hit.png"],
    },
    "fly": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/fly.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/fly_fly.png"],
        "damage": [f"{EXTENDED_ENEMY_ROOT}/fly_hit.png"],
    },
    "boss_block": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/slimeBlock.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/slimeBlock.png"],
        "damage": [f"{EXTENDED_ENEMY_ROOT}/slime_hit.png"],
    },
    "bat": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/bat.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/bat_fly.png"],
        "damage": [f"{EXTENDED_ENEMY_ROOT}/bat_hit.png"],
    },
    "ghost": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/ghost.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/ghost.png"],
        "damage": [f"{EXTENDED_ENEMY_ROOT}/ghost_hit.png"],
    },
    "boss_ghost": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/ghost.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/ghost.png"],
        "damage": [f"{EXTENDED_ENEMY_ROOT}/ghost_hit.png"],
    },
    "alien1": {
        "idle": f"{ALIEN_ROOT}/alienBeige_stand.png",
        "walk": [
            f"{ALIEN_ROOT}/alienBeige_walk1.png",
            f"{ALIEN_ROOT}/alienBeige_walk2.png",
        ],
        "damage": [f"{ALIEN_ROOT}/alienBeige_hurt.png"],
    },
    "alien2": {
        "idle": f"{ALIEN_ROOT}/alienBlue_stand.png",
        "walk": [
            f"{ALIEN_ROOT}/alienBlue_walk1.png",
            f"{ALIEN_ROOT}/alienBlue_walk2.png",
        ],
        "damage": [f"{ALIEN_ROOT}/alienBlue_hurt.png"],
    },
    "alien3": {
        "idle": f"{ALIEN_ROOT}/alienGreen_stand.png",
        "walk": [
            f"{ALIEN_ROOT}/alienGreen_walk1.png",
            f"{ALIEN_ROOT}/alienGreen_walk2.png",
        ],
        "damage": [f"{ALIEN_ROOT}/alienGreen_hurt.png"],
    },
    "alien4": {
        "idle": f"{ALIEN_ROOT}/alienPink_stand.png",
        "walk": [
            f"{ALIEN_ROOT}/alienPink_walk1.png",
            f"{ALIEN_ROOT}/alienPink_walk2.png",
        ],
        "damage": [f"{ALIEN_ROOT}/alienPink_hurt.png"],
    },
    "alien5": {
        "idle": f"{ALIEN_ROOT}/alienYellow_stand.png",
        "walk": [
            f"{ALIEN_ROOT}/alienYellow_walk1.png",
            f"{ALIEN_ROOT}/alienYellow_walk2.png",
        ],
        "damage": [f"{ALIEN_ROOT}/alienYellow_hurt.png"],
    },
    "saucer1": {
        "idle": f"{SAUCER_ROOT}/shipBeige_manned.png",
        "walk": [f"{SAUCER_ROOT}/shipBeige_manned.png"],
        "damage": [
            f"{SAUCER_ROOT}/shipBeige_damage1.png",
            f"{SAUCER_ROOT}/shipBeige_damage2.png",
        ],
    },
    "saucer2": {
        "idle": f"{SAUCER_ROOT}/shipBlue_manned.png",
        "walk": [f"{SAUCER_ROOT}/shipBlue_manned.png"],
        "damage": [
            f"{SAUCER_ROOT}/shipBlue_damage1.png",
            f"{SAUCER_ROOT}/shipBlue_damage2.png",
        ],
    },
    "saucer3": {
        "idle": f"{SAUCER_ROOT}/shipGreen_manned.png",
        "walk": [f"{SAUCER_ROOT}/shipGreen_manned.png"],
        "damage": [
            f"{SAUCER_ROOT}/shipGreen_damage1.png",
            f"{SAUCER_ROOT}/shipGreen_damage2.png",
        ],
    },
    "saucer4": {
        "idle": f"{SAUCER_ROOT}/shipPink_manned.png",
        "walk": [f"{SAUCER_ROOT}/shipPink_manned.png"],
        "damage": [
            f"{SAUCER_ROOT}/shipPink_damage1.png",
            f"{SAUCER_ROOT}/shipPink_damage.png",
        ],
    },
    "saucer5": {
        "idle": f"{SAUCER_ROOT}/shipYellow_manned.png",
        "walk": [f"{SAUCER_ROOT}/shipYellow_manned.png"],
        "damage": [
            f"{SAUCER_ROOT}/shipYellow_damage1.png",
            f"{SAUCER_ROOT}/shipYellow_damage2.png",
        ],
    },
    "robobowser": {
        "idle": f"{ROBOWSER_ROOT}/character_robot_idle.png",
        "walk": [
            f"{ROBOWSER_ROOT}/character_robot_walk{i}.png"
            for i in range(8)
        ],
        "damage": [f"{ROBOWSER_ROOT}/character_robot_hit.png"],
    },
}

DEFAULT_CONTACT_DAMAGE = 10
BOSS_CONTACT_DAMAGE = {
    "boss_ghost": 20,
    "boss_block": 20,
    "robobowser": 30,
}

class EnemyManager:
    """Create runtime enemies from markers in a level's tilemap."""

    def __init__(self):
        self.enemy_list = arcade.SpriteList()

    def load_enemies(self, level):
        self.enemy_list = arcade.SpriteList()
        enemy_markers = []

        try:
            sprite_markers = level.scene.get_sprite_list("Enemies")
        except KeyError:
            sprite_markers = ()

        for marker in sprite_markers:
            enemy_markers.append((marker.properties, marker.position))

        # Tiled point markers are loaded as objects rather than Scene sprites.
        for marker in level.tile_map.object_lists.get("Enemies", ()):
            if isinstance(marker.shape, tuple) and len(marker.shape) == 2:
                enemy_markers.append((marker.properties or {}, marker.shape))

        tile_distance = level.tile_map.tile_width * level.tile_map.scaling

        for properties, marker_position in enemy_markers:
            enemy = self._create_enemy(properties, marker_position, tile_distance)
            if enemy is not None:
                self.enemy_list.append(enemy)

        if "Enemies" in level.scene:
            level.scene.remove_sprite_list_by_name("Enemies")
        level.scene.add_sprite_list("Enemies", sprite_list=self.enemy_list)
        return self.enemy_list

    def check_for_enemy_collision(self, player, lock_list, physics_manager):
        """Resolve damage and cleanup when the player touches enemies."""
        enemies_hit = arcade.check_for_collision_with_list(player, self.enemy_list)

        if not enemies_hit:
            return

        contact_damage = max(
            BOSS_CONTACT_DAMAGE.get(enemy.enemy_type, DEFAULT_CONTACT_DAMAGE)
            for enemy in enemies_hit
        )
        player.take_damage(contact_damage)
        for enemy in enemies_hit:
            enemy.take_damage(25)
            if enemy.health <= 0:
                if enemy.enemy_type == "robobowser":
                    lock_list.clear()
                enemy.remove_from_sprite_lists()
                physics_manager.remove_enemy(enemy)

    @staticmethod
    def _create_enemy(properties, marker_position, tile_distance):
        enemy_type_value = properties.get("type")
        if not isinstance(enemy_type_value, str):
            print("Skipping enemy marker with no type")
            return None

        enemy_type = enemy_type_value.lower().replace("-", "_")

        if enemy_type in ENEMY_TEXTURES:
            robot_color = ROBOT_DAMAGE_TEXTURES[enemy_type]
            enemy = Enemy(
                ENEMY_TEXTURES[enemy_type],
                2,
                damage_paths=[
                    f"{ROBOT_TEXTURE_ROOT}/robot_{robot_color}Damage1.png",
                    f"{ROBOT_TEXTURE_ROOT}/robot_{robot_color}Damage2.png",
                ],
            )
            enemy.scale = 0.3
        elif enemy_type in EXTENDED_ENEMY_ANIMATIONS:
            animation = EXTENDED_ENEMY_ANIMATIONS[enemy_type]
            enemy = Enemy(
                idle_path=animation["idle"],
                walk_paths=animation["walk"],
                damage_paths=animation.get("damage"),
                invert_facing=enemy_type in ("snail", "slime", "fly"),
            )
            if enemy_type == "robobowser":
                enemy.scale = 1.5
            elif enemy_type in ("boss_ghost", "boss_block"):
                enemy.scale = 1.0
            else:
                enemy.scale = 0.5
            enemy.is_flying = enemy_type in ("bat", "fly") or enemy_type.startswith(
                "saucer"
            )
        else:
            print(f"Skipping unknown enemy type: {enemy_type}")
            return None

        enemy.enemy_type = enemy_type
        enemy.position = marker_position
        enemy.change_x = properties.get("change_x", ENEMY_SPEED)

        if "boundary_left" in properties and "boundary_right" in properties:
            enemy.set_patrol_range(
                marker_position[0] - properties["boundary_left"] * tile_distance,
                marker_position[0] + properties["boundary_right"] * tile_distance,
            )

        return enemy

```