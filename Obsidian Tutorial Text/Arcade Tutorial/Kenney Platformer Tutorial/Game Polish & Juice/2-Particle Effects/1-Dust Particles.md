
I found the arcade particle system. We will use it to generate dust particles.

```python title=dust.py
import random

import arcade
from arcade import particles

from .player import Dir, State


DUST_COLORS = (
    (201, 184, 151, 255),
    (184, 166, 132, 255),
    (218, 207, 181, 255),
)


class DustManager:
    """Create and manage procedural Arcade particle emitters for the player."""

    RUN_INTERVAL = 0.2
    PARTICLE_COUNTS = {"run": 5, "jump": 9, "fall": 12}

    def __init__(self, player):
        self.player = player
        self.emitters = []
        self.run_timer = 0.0
        self.was_falling = False
        self.was_grounded = False
        self.textures = tuple(
            arcade.make_soft_circle_texture(diameter, color)
            for diameter, color in zip((16, 20, 24), DUST_COLORS)
        )

    def spawn_jump(self):
        self._spawn("jump")

    def update(self, delta_time, grounded):
        if grounded and not self.was_grounded and self.was_falling:
            self._spawn("fall")

        if grounded and self.player.current_state == State.WALK:
            self.run_timer -= delta_time
            if self.run_timer <= 0:
                self._spawn(
                    "run",
                    facing_left=self.player.current_direction == Dir.LEFT,
                )
                self.run_timer = self.RUN_INTERVAL
        else:
            self.run_timer = 0.0

        self.was_falling = self.player.current_state == State.FALL
        self.was_grounded = grounded

        for emitter in tuple(self.emitters):
            emitter.update(delta_time)
            if emitter.can_reap():
                self.emitters.remove(emitter)

    def draw(self):
        for emitter in self.emitters:
            emitter.draw()

    def _spawn(self, animation, facing_left=False):
        trail_offset = 0
        horizontal_direction = 0
        if animation == "run":
            trail_offset = 12 if facing_left else -12
            horizontal_direction = 1 if facing_left else -1

        def create_particle(emitter):
            if animation == "run":
                change_x = horizontal_direction * random.uniform(0.15, 0.55)
                change_y = random.uniform(0.08, 0.3)
            else:
                change_x = random.uniform(-0.55, 0.55)
                change_y = random.uniform(0.12, 0.5)

            return particles.FadeParticle(
                filename_or_texture=random.choice(self.textures),
                change_xy=(change_x, change_y),
                lifetime=random.uniform(0.35, 0.6),
                center_xy=(random.uniform(-8, 8), random.uniform(0, 4)),
                scale=random.uniform(0.35, 0.75),
                start_alpha=random.randint(110, 185),
                end_alpha=0,
            )

        self.emitters.append(
            particles.Emitter(
                center_xy=(
                    self.player.center_x + trail_offset,
                    self.player.bottom + 2,
                ),
                emit_controller=particles.EmitBurst(
                    self.PARTICLE_COUNTS[animation]
                ),
                particle_factory=create_particle,
            )
        )

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
        self.game_manager.restore_player_state(self.player, self.hud_camera)
        self.player.position = (CAMERA_WIDTH/2, CAMERA_HEIGHT/2)

        self.level = self.game_manager.create_level()
        self.game_manager.configure_player(self.player)
        self.level.level_setup(self.player, self.camera)

        self.enemy_list = self.level.enemy_list
        self.physics_manager = self.level.physics_manager
        self.leaf_manager = self.level.leaf_manager
        self.dust_manager = self.level.dust_manager

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.camera.draw_background()
        self.level.scene.draw(pixelated=True)
        self.dust_manager.draw()
        self.player.draw_health_bar()
        for enemy in self.enemy_list:
            enemy.draw_health_bar()

        self.hud_camera.draw()

    def on_update(self, delta_time):
        player_was_moving_up = self.player.change_y > 0
        self.physics_manager.update_player()
        self.level.check_for_block_hit(self.player, player_was_moving_up)
        self.player.keep_in_level(self.level.tile_map)

        if self.game_manager.check_for_player_death(self.player):
            return

        if self.level.check_for_exit(self.player):
            self.game_manager.complete_level(self.player)
            return

        self.level.collect_coins(self.player, self.hud_camera)
        self.level.collect_stars(self.player, self.hud_camera)
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
        self.player.update_state(
            delta_time,
            on_moving_platform=self.physics_manager.player_on_moving_platform,
        )
        self.player.on_update(delta_time)  # Sets the player direction and animation
        self.dust_manager.update(
            delta_time,
            grounded=self.physics_manager.player_is_grounded,
        )
        self.camera.follow(self.player)
        self.leaf_manager.update(delta_time, self.camera)

    def on_key_press(self, key, key_modifiers):
        if key in (arcade.key.W, arcade.key.UP, arcade.key.SPACE):
            if self.physics_manager.jump():
                self.dust_manager.spawn_jump()
                     
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

from .dust import DustManager
from .enemy_manager import EnemyManager
from .leaf import LeafManager
from .nature import load_nature
from .physics import PhysicsManager
from .settings import MOVING_PLATFORM_SPEED


PRINCESS_IDLE_PATH = (
    "assets/kenney_assets/Toon Characters/Female person/PNG/Poses/"
    "character_femalePerson_idle.png"
)
STAR_PATH = (
    Path(__file__).resolve().parent.parent
    / "assets/kenney_assets/New Platformer Pack/Sprites/Tiles/Default/star.png"
)
BLOCK_TILE_IDS = {1, 16, 19}


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
        self.star_list = arcade.SpriteList()
        self.revealed_block_ids = set()
        self.scene.add_sprite_list("Stars", sprite_list=self.star_list)
        self.dust_manager = DustManager(player)

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

    def collect_stars(self, player, hud_camera):
        """Collect revealed stars and award ten coins for each one."""
        stars_hit = arcade.check_for_collision_with_list(player, self.star_list)

        for star in stars_hit:
            star.remove_from_sprite_lists()
            player.coins += 10
            hud_camera.set_score(player.coins)

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

    def check_for_block_hit(self, player, was_moving_up):
        """Reveal a star when the player bumps a Block from underneath."""
        if self.name != "level_01" or not was_moving_up:
            return

        for block in self.moving_platforms:
            block_type = str(
                block.properties.get("type", block.properties.get("Type", ""))
            ).lower()
            is_block = (
                block_type == "block"
                or block.properties.get("tile_id") in BLOCK_TILE_IDS
            )
            if not is_block or id(block) in self.revealed_block_ids:
                continue

            overlaps_horizontally = player.right > block.left and player.left < block.right
            touches_underside = abs(player.top - block.bottom) <= 4
            if not (overlaps_horizontally and touches_underside):
                continue

            star = arcade.Sprite(STAR_PATH)
            star.center_x = block.center_x
            star.bottom = block.top
            self.star_list.append(star)
            self.revealed_block_ids.add(id(block))
            break

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