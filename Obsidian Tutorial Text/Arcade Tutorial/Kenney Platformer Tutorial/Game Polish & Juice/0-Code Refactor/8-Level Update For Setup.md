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
        if self.name == "level_03":
            player.scale = 0.5
        self.scene.add_sprite("Player", player)
        camera.set_limits_to_tilemap(self.tile_map)

        self.moving_platforms = self.get_layer("Moving Platforms")
        self.exit_list = self.get_layer("Exit")
        self.hazard_list = self.get_layer("Hazards")
        self.ladder_list = self.get_layer("Ladders")
        self.lock_list = self.get_layer("Locks")
        self.coin_list = self.get_layer("Coins")

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
        self.player.position = (CAMERA_WIDTH/2, CAMERA_HEIGHT/2)
        self.player.scale = 0.5

        self.level = self.game_manager.create_level()
        self.level.level_setup(self.player, self.camera)

        self.exit_list = self.level.exit_list
        self.hazard_list = self.level.hazard_list
        self.lock_list = self.level.lock_list
        self.coin_list = self.level.coin_list
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