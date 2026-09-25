```python title=leaf.py
import random

import arcade

from .nature import ASSET_ROOT, AnimatedNatureSprite
from .settings import CAMERA_HEIGHT, CAMERA_WIDTH


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
        bottom = camera_y - CAMERA_HEIGHT / 2

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

        left = camera_x - CAMERA_WIDTH / 2
        top = camera_y + CAMERA_HEIGHT / 2
        leaf = Leaf(
            random.uniform(left, left + CAMERA_WIDTH),
            top + 8,
        )
        self.leaf_list.append(leaf)

```

```python title=nature.py
from pathlib import Path
import random

import arcade


ASSET_ROOT = Path(__file__).resolve().parent.parent / "assets"
NATURE_TEXTURE_ROOT = ASSET_ROOT / "NatureAssets"


class AnimatedNatureSprite(arcade.Sprite):
    """Base class for nature sprites that loop through numbered textures."""

    texture_root = NATURE_TEXTURE_ROOT
    texture_folder: str
    frame_count = 16
    first_frame = 1
    filename_digits = 4
    seconds_per_frame = 0.12
    randomize_animation = False

    def __init__(self, x: float, y: float):
        super().__init__()

        texture_dir = self.texture_root / self.texture_folder
        self.textures = [
            arcade.load_texture(
                texture_dir / f"{frame:0{self.filename_digits}}.png"
            )
            for frame in range(
                self.first_frame,
                self.first_frame + self.frame_count,
            )
        ]
        self.current_frame = (
            random.randrange(self.frame_count) if self.randomize_animation else 0
        )
        self.texture = self.textures[self.current_frame]
        self.position = x, y
        self.animation_time = (
            random.uniform(0, self.seconds_per_frame)
            if self.randomize_animation
            else 0.0
        )

    def update_animation(self, delta_time: float = 1 / 60):
        self.animation_time += delta_time

        if self.animation_time >= self.seconds_per_frame:
            self.animation_time = 0.0
            self.current_frame = (self.current_frame + 1) % len(self.textures)
            self.texture = self.textures[self.current_frame]


class Grass(AnimatedNatureSprite):
    texture_folder = "grass_2"


class Reeds(AnimatedNatureSprite):
    texture_folder = "grass_3"


class Bush(AnimatedNatureSprite):
    texture_folder = "bush_1"


class Tree(AnimatedNatureSprite):
    texture_folder = "tree_1"


def load_nature(level):
    """Replace a level's tilemap markers with animated nature sprites."""
    nature_classes = {
        "Grass": Grass,
        "Tree": Tree,
        "Bush": Bush,
        "Reed": Reeds,
    }
    nature_list = arcade.SpriteList()

    try:
        nature_markers = level.scene.get_sprite_list("Nature")
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

    if "Nature" in level.scene:
        level.scene.remove_sprite_list_by_name("Nature")
    level.scene.add_sprite_list("Nature", sprite_list=nature_list)
    return nature_list

```

```python title=game.py
import arcade
import sys
from pathlib import Path

# Allow this tutorial file to be run directly from its subdirectory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from library import GameCamera, HudCamera, Player
from library.enemy_manager import EnemyManager
from library.game_manager import GameManager
from library.leaf import LeafManager
from library.nature import load_nature
from library.physics import PhysicsManager
from library.settings import *

WINDOW_TITLE = "Kenney Platformer Tutorial"
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

        self.physics_manager = PhysicsManager(
            self.player,
            self.enemy_list,
            moving_platforms=self.moving_platforms,
            player_walls=[self.level.scene["Platforms"], self.lock_list],
            enemy_walls=self.level.scene["Platforms"],
            ladders=self.ladder_list,
        )

        self.camera.follow(self.player)

        self.nature_list = load_nature(self.level)

        self.leaf_manager = LeafManager(self.level)

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
        self.physics_manager.update_player()
        self.keep_player_in_level()

        if self.check_for_exit():
            return

        self.collect_coins()
        self.check_for_hazard_collision()

        self.physics_manager.update_enemies()
        self.check_for_enemy_collision()

        for enemy in self.enemy_list:
            enemy.on_update(delta_time)

        self.level.scene.update_animation(delta_time)
        self.player.update_state(delta_time)
        self.player.on_update(delta_time)  # Sets the player direction and animation
        self.camera.follow(self.player)
        self.leaf_manager.update(delta_time, self.camera)

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
                    self.physics_manager.remove_enemy(enemy)

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
    game_manager.start_game()
    arcade.run()  # Runs the Arcade game loop

if __name__ == "__main__":
    main()

```